import base64
import os
import random
import logging
import re
from typing import List, Optional
from app.config import settings
from google.genai.errors import ClientError

logger = logging.getLogger(__name__)

# Try to import Google GenAI SDK
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    if settings.GEMINI_API_KEY:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        GENAI_AVAILABLE = True
        logger.info("Google GenAI client initialized successfully.")
    else:
        logger.warning("GEMINI_API_KEY not found. Running in OFFLINE MOCK MODE.")
except Exception as e:
    logger.warning(f"Failed to initialize Google GenAI SDK: {e}. Running in OFFLINE MOCK MODE.")

class GeminiService:
    @staticmethod
    def generate_chat_response(
        prompt: str,
        history: Optional[List[dict]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        if GENAI_AVAILABLE:
            try:
                # Prepare history for the API
                contents = []
                if history:
                    for h in history[-10:]:  # Keep last 10 turns
                        role = "user" if h["role"] == "user" else "model"
                        contents.append(types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=h["message"])]
                        ))

                # Append current prompt
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                ))

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=config
                )
                if getattr(response, "text", None):
                    return response.text
            except Exception as e:
                logger.error(f"Gemini API chat error: {e}. Falling back to mock response.", exc_info=True)

        # OFFLINE MOCK MODE CHAT RESPONSE
        return GeminiService._generate_mock_chat(prompt, system_instruction)

    @staticmethod
    def generate_text_response(prompt: str, context: str = "") -> str:
        """Generate a high-speed text answer using Gemini 2.0 Flash with streaming support."""
        if GENAI_AVAILABLE:
            try:
                # Attempt streaming if the SDK supports it
                if hasattr(client, "responses") and hasattr(client.responses, "stream"):
                    logger.info("Starting Gemini text stream generation.")
                    chunks: List[str] = []
                    stream = client.responses.stream(
                        model="gemini-2.0-flash",
                        input=[
                            {"role": "system", "content": [{"type": "text", "text": context}]},
                            {"role": "user", "content": [{"type": "text", "text": prompt}]}
                        ] if context else [
                            {"role": "user", "content": [{"type": "text", "text": prompt}]}
                        ],
                        temperature=0.7,
                    )
                    for event in stream:
                        text_delta = None
                        if hasattr(event, "type") and getattr(event, "type") == "error":
                             logger.error(f"Stream error: {event}")
                             break
                        
                        if hasattr(event, "type") and getattr(event, "type") == "response.output_text.delta":
                            text_delta = getattr(event, "delta", None)
                        elif hasattr(event, "response"):
                            response_obj = getattr(event, "response")
                            text_delta = getattr(response_obj, "output_text", None)
                        elif isinstance(event, dict):
                            response_obj = event.get("response", {})
                            text_delta = response_obj.get("output_text") or response_obj.get("delta")

                        if isinstance(text_delta, str):
                            chunks.append(text_delta)
                    streamed_text = "".join(chunks).strip()
                    if streamed_text:
                        return streamed_text

                # Fallback to standard non-streaming generation
                contents = []
                if context:
                    contents.append(types.Content(
                        role="system",
                        parts=[types.Part.from_text(text=context)]
                    ))
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                ))

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                    )
                )
                if getattr(response, "text", None):
                    return response.text
            except Exception as e:
                logger.error(f"Gemini text generation error: {e}", exc_info=True)

        logger.warning("Gemini unavailable or failed, returning fallback text response.")
        return GeminiService._generate_mock_chat(prompt, context)

    @staticmethod
    def generate_image_response(prompt: str) -> str:
        """Generate an image using HuggingFace as primary, Imagen fallback."""
        from app.services.huggingface_service import HuggingFaceImageService
        hf_service = HuggingFaceImageService()
        
        # Primary: Try Hugging Face
        img_bytes = hf_service.generate_image(prompt)
        if img_bytes:
            base64_str = base64.b64encode(img_bytes).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_str}"

        # Secondary: Try Gemini/Imagen
        if GENAI_AVAILABLE:
            try:
                result = client.models.generate_images(
                    model="imagen-4.0-generate-001",
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg",
                        aspect_ratio="1:1"
                    )
                )
                generated_images = getattr(result, "generated_images", []) or []
                if generated_images:
                    image_obj = generated_images[0]
                    img_bytes = getattr(getattr(image_obj, "image", None), "image_bytes", None)
                    if img_bytes:
                        base64_str = base64.b64encode(img_bytes).decode("utf-8")
                        return f"data:image/jpeg;base64,{base64_str}"
            except Exception as e:
                logger.warning(f"AI Image generation failed (likely quota): {e}")

        # Final Fallback: Advanced Stylized SVG
        return GeminiService._generate_mock_svg(prompt)

    @staticmethod
    def generate_embeddings(text: str) -> List[float]:
        if GENAI_AVAILABLE:
            try:
                response = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=text
                )
                if response.embeddings:
                    return response.embeddings[0].values
            except ClientError as e:
                if e.status_code == 429:
                    logger.warning("Quota exhausted (429) in embeddings. Falling back immediately.")
                else:
                    logger.error(f"Gemini Embeddings error: {e}")
            except Exception as e:
                logger.error(f"Gemini Embeddings unexpected error: {e}")

        # OFFLINE MOCK MODE EMBEDDINGS (768 dimensions)
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

    @staticmethod
    def generate_image(prompt: str, style: str = "oil painting") -> str:
        enhanced_prompt = f"A beautiful {style} of {prompt}, majestic, warm lighting, sacred atmosphere, highly detailed"
        return GeminiService.generate_image_response(enhanced_prompt)

    @staticmethod
    def _generate_mock_chat(prompt: str, system_instruction: str = None) -> str:
        prompt_lower = prompt.lower()
        
        # Extract denomination from system_instruction if possible
        denomination = "Protestant"
        if system_instruction:
            for d in ["Catholic", "Orthodox", "Protestant"]:
                if d in system_instruction:
                    denomination = d
                    break

        # Check if this is an image enhancement request
        if "enhance this prompt" in prompt_lower:
            # Extract the actual prompt
            match = re.search(r"enhance this prompt: '(.+)' in the style: '(.+)'", prompt_lower)
            if match:
                raw_p, style = match.groups()
                return f"A majestic {style} depicting {raw_p}, featuring sacred volumetric lighting, highly detailed textures, and a profound spiritual atmosphere."
            return f"A beautiful sacred art piece depicting the requested theme with divine light and intricate detail."

        # Scripture check questions
        if "john 3:16" in prompt_lower:
            return "John 3:16 says: 'For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life.' This is a cornerstone of Christian faith representing the core message of salvation through Christ."
        
        if "death" in prompt_lower or "afterlife" in prompt_lower or "what happens after death" in prompt_lower:
            views = {
                "Protestant": "Believers go immediately to the presence of Christ in Heaven based on faith alone (sola fide). There is no purgatory. At the final judgment, there is physical resurrection to eternal life with God or eternal separation.",
                "Catholic": "At death, the soul undergoes particular judgment. Those fully purified enter Heaven. Those dying in God's grace but with venial sins enter Purgatory for purification before entering Heaven. Those in mortal sin enter Hell. The final judgment brings bodily resurrection.",
                "Orthodox": "The soul enters an intermediate state (neither full heaven nor full hell) awaiting the general resurrection. Prayers for the departed are offered, trusting in God's mercy, but the concept of Purgatory as a forensic place of debt-payment is not held. Instead, it is seen as a continuation of spiritual growth (theosis)."
            }
            primary_view = views.get(denomination, views["Protestant"])
            other_views = "\n\n".join([f"**{d} View**:\n{v}" for d, v in views.items() if d != denomination])
            return (
                f"Regarding life after death, here is the **{denomination}** perspective:\n\n"
                f"{primary_view}\n\n"
                f"--- Brief comparison with other traditions ---\n\n"
                f"{other_views}"
            )
            
        if "james 2" in prompt_lower or "faith and works" in prompt_lower:
            views = {
                "Protestant": "Faith alone justifies, but true saving faith naturally produces good works. Works are the fruit, not the root of salvation (Ephesians 2:8-9).",
                "Catholic": "Justification is a process. Faith and charity/good works are both necessary. Saving faith is 'faith working through love' (Galatians 5:6).",
                "Orthodox": "Faith and works are inseparable aspects of a single life in Christ. Salvation is a dynamic, lifelong process of synergistic cooperation between human free will and God's grace."
            }
            primary_view = views.get(denomination, views["Protestant"])
            other_views = "\n\n".join([f"**{d} View**:\n{v}" for d, v in views.items() if d != denomination])
            
            return (
                f"James 2:14-26 addresses the relationship of faith and works from the **{denomination}** perspective:\n\n"
                f"{primary_view}\n\n"
                f"--- Brief comparison with other traditions ---\n\n"
                f"{other_views}"
            )
            
        if "sermon" in prompt_lower:
            return (
                "# Sermon: The Path of Trust (Proverbs 3:5-6)\n\n"
                "**Introduction**\n"
                "Grace and peace to you, brothers and sisters. Today, we reflect on one of the most comforting scriptures: 'Trust in the Lord with all your heart, and lean not on your own understanding...'\n\n"
                "**Point 1: Total Trust**\n"
                "To trust with 'all your heart' means holding nothing back. In times of uncertainty, our natural instinct is to control. But scripture calls us to release control to the Father.\n\n"
                "**Point 2: Releasing Our Understanding**\n"
                "Our vision is limited. God's vision is infinite. When we lean on our own understanding, we create anxiety. When we lean on God, we find peace.\n\n"
                "**Conclusion & Prayer**\n"
                "May you walk this week with a heart surrendered to Him, knowing He will direct your paths. Amen."
            )
            
        if "devotional" in prompt_lower:
            return (
                "## Daily Devotional: Grounded in Love\n\n"
                "**Scripture Focus: Ephesians 3:17-18**\n"
                "*'...that Christ may dwell in your hearts through faith; that you, being rooted and grounded in love, may be able to comprehend...'* \n\n"
                "**Reflection**\n"
                "Consider a massive oak tree. It stands firm during severe storms because its roots run deep and wide. In the same way, the Apostle Paul prays that our lives would be 'rooted and grounded' in Christ's love. This love isn't a fleeting emotion; it is the absolute foundation of who we are.\n\n"
                "**Application**\n"
                "Today, whenever you feel a wave of anxiety, take a deep breath and whisper: 'I am rooted and grounded in God's love.' Let that truth settle your spirit.\n\n"
                "**Prayer**\n"
                "Lord, let my roots sink deep into the soil of Your love today. Secure my identity in You. Amen."
            )

        return (
            "Thank you for your question about Christian faith and scripture. As a theological assistant, "
            "I am grounded in Biblical teaching. If you have questions about specific verses, theological topics, "
            "or want to generate devotional content, please feel free to ask. "
            "Remember that scripture provides a foundation for faith: 'Thy word is a lamp unto my feet, and a light unto my path.' (Psalm 119:105)."
        )

    @staticmethod
    def _generate_mock_svg(prompt: str) -> str:
        import base64
        prompt_lower = prompt.lower()
        
        # 1. Sanity check: If prompt is gibberish or too short
        if len(prompt.strip()) < 8 or "nnnnnnnn" in prompt_lower:
            return GeminiService._generate_placeholder_svg("Awaiting Art Request")
        
        style = "standard"
        if "oil" in prompt_lower: style = "oil"
        elif "glass" in prompt_lower or "stained" in prompt_lower: style = "glass"
        
        # Color palettes
        gold = "#D4AF37"
        dark_gold = "#A87C11"
        slate = "#1E293B"
        cream = "#FDFBF7"
        amber = "#F5A623"
        crimson = "#8B0000"
        lion_orange = "#C2410C"
        
        # Determine artwork theme
        theme_title = "FAITHGUIDE SACRED ART"
        content_shapes = ""
        
        if "daniel" in prompt_lower or "lion" in prompt_lower:
            theme_title = "DANIEL IN THE LIONS' DEN"
            content_shapes = f"""
                <path d="M 50 400 Q 200 50 350 400" fill="#1E293B" opacity="0.5"/>
                <path d="M 190 300 Q 200 270 210 300 L 210 350 L 190 350 Z" fill="{cream}"/>
                <circle cx="200" cy="285" r="10" fill="{cream}"/>
                <circle cx="100" cy="320" r="15" fill="{lion_orange}"/>
                <circle cx="300" cy="340" r="15" fill="{lion_orange}"/>
                <path d="M 150 0 L 250 0 L 220 280 L 180 280 Z" fill="{amber}" opacity="0.2"/>
            """
        elif "cross" in prompt_lower or "salvation" in prompt_lower or "christ" in prompt_lower:
            theme_title = "THE MAJESTIC CROSS"
            content_shapes = f"""
                <circle cx="200" cy="200" r="140" fill="none" stroke="{gold}" stroke-width="2" opacity="0.3"/>
                <path d="M 185 80 L 215 80 L 215 155 L 290 155 L 290 185 L 215 185 L 215 320 L 185 320 L 185 185 L 110 185 L 110 155 L 185 155 Z" 
                      fill="{gold}" stroke="{dark_gold}" stroke-width="3"/>
            """
        else:
            theme_title = "SACRED SCRIPTURES"
            content_shapes = f"""
                <rect x="100" y="100" width="200" height="180" rx="10" fill="{crimson}" stroke="{gold}" stroke-width="3"/>
                <path d="M 110 110 C 150 115, 200 110, 200 120 C 200 110, 250 115, 290 110 L 290 260 C 250 265, 200 260, 200 270 C 200 260, 150 265, 110 260 Z" fill="{cream}"/>
            """

        # Apply Filters based on style
        filter_defs = ""
        style_attr = ""
        if style == "oil":
            filter_defs = """
                <filter id="oilFilter">
                    <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" result="noise"/>
                    <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" />
                </filter>
            """
            style_attr = 'filter="url(#oilFilter)"'
        elif style == "glass":
            filter_defs = f"""
                <filter id="glassFilter">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur"/>
                    <feSpecularLighting in="blur" surfaceScale="5" specularConstant="1" specularExponent="20" lighting-color="white" result="light">
                        <fePointLight x="-5000" y="-10000" z="20000"/>
                    </feSpecularLighting>
                    <feComposite in="light" in2="SourceAlpha" operator="in" result="lightInAlpha"/>
                    <feComposite in="SourceGraphic" in2="lightInAlpha" operator="arithmetic" k1="0" k2="1" k3="1" k4="0"/>
                </filter>
                <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="black" stroke-width="1.5" opacity="0.4"/>
                </pattern>
            """
            style_attr = 'filter="url(#glassFilter)"'
            content_shapes += '<rect width="400" height="400" fill="url(#grid)" />'

        svg_content = f"""
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
                <defs>{filter_defs}</defs>
                <rect width="400" height="400" fill="{slate}"/>
                <g {style_attr}>
                    {content_shapes}
                </g>
                <text x="200" y="370" fill="{cream}" font-family="serif" font-size="14" text-anchor="middle" letter-spacing="1">{theme_title}</text>
                <text x="200" y="385" fill="{gold}" font-family="sans-serif" font-size="8" text-anchor="middle" opacity="0.8">MODE: {style.upper()} ART</text>
            </svg>
        """
            
        base64_svg = base64.b64encode(svg_content.strip().encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{base64_svg}"

    @staticmethod
    def _generate_placeholder_svg(text: str) -> str:
        import base64
        svg_content = f"""
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
                <rect width="400" height="400" fill="#0F172A"/>
                <text x="200" y="200" fill="#D4AF37" font-family="sans-serif" font-size="20" text-anchor="middle">{text}</text>
            </svg>
        """
        base64_svg = base64.b64encode(svg_content.strip().encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{base64_svg}"



