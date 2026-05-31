import os
import logging
from typing import Optional
from app.config import settings
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Client
GROQ_CLIENT = None
if settings.GROQ_API_KEY:
    try:
        GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Groq: {e}")

class LLMService:
    @staticmethod
    def generate_chat_response(prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates a chat response using Groq. Raises exceptions on failure to allow EvalService fallback."""
        if not GROQ_CLIENT:
            raise Exception("Groq API key not configured.")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        # Groq will raise an APIError/RateLimitError on failure
        chat_completion = GROQ_CLIENT.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content

    @staticmethod
    def generate_image(prompt: str, style: str = "oil painting") -> str:
        """Generate an image using HuggingFace as primary, falling back to Vector engine."""
        from app.services.huggingface_service import HuggingFaceImageService
        from app.services.gemini_service import GeminiService
        import base64
        
        hf_service = HuggingFaceImageService()
        
        # Tier 2: Attempt HuggingFace Cloud Generation
        try:
            img_bytes = hf_service.generate_image(prompt)
            if img_bytes:
                base64_str = base64.b64encode(img_bytes).decode("utf-8")
                return f"data:image/jpeg;base64,{base64_str}"
            logger.warning("HuggingFace generation failed, falling back to Vector engine.")
        except Exception as e:
            logger.error(f"HuggingFace service error: {e}")
            
        # Tier 3: Fallback to stylized vector engine
        return GeminiService._generate_mock_svg(prompt)
