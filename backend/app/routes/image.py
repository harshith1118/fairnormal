from fastapi import APIRouter, HTTPException
from app.models import ImageRequest, ImageResponse
from app.services.safety_service import SafetyService
from app.services.llm_service import LLMService

router = APIRouter()

@router.post("/image", response_model=ImageResponse)
async def generate_image_endpoint(request: ImageRequest):
    raw_prompt = request.prompt
    style = request.style
    
    # 1. FORCE SECURITY CHECK FIRST (Before Enhancement or Generation)
    safety_check = SafetyService.evaluate_prompt(f"Image generation request: {raw_prompt}")
    if safety_check["status"] == "REFUSE":
        # Block and refuse immediately with explicit status
        return ImageResponse(
            image_url=None,
            base64_image=None,
            enhanced_prompt=raw_prompt,
            safety_status="REFUSE",
            safety_reason="Prompt flagged by security gateway."
        )
        
    # 2. Dynamic Prompt Enhancement
    enhanced_prompt = raw_prompt
    if request.enhance:
        system_instruction = (
            "You are an art director specializing in Christian sacred art.\n"
            "Your task is to take a simple drawing prompt and enhance it for a high-quality "
            "text-to-image generator. Expand the description by adding artistic terms, "
            "sacred atmospheres, warm volumetric lighting, soft color contrasts, and biblically "
            "faithful details. Keep it deeply respectful, beautiful, and awe-inspiring.\n"
            "Return ONLY the enhanced prompt string. Do not include markdown codeblocks or quotes."
        )
        try:
            enhanced_prompt = LLMService.generate_chat_response(
                prompt=f"Enhance this prompt: '{raw_prompt}' in the style: '{style}'",
                system_instruction=system_instruction
            )
            enhanced_prompt = enhanced_prompt.strip().replace('"', '')
        except Exception as e:
            # Fallback to standard style expansion
            enhanced_prompt = f"A gorgeous {style} depicting {raw_prompt}, majestic, high resolution, sacred volumetric light"

    # 3. Generate Image
    try:
        base64_img = LLMService.generate_image(enhanced_prompt, style=style)
        return ImageResponse(
            base64_image=base64_img,
            enhanced_prompt=enhanced_prompt,
            safety_status="ALLOW",
            safety_reason="Passed image generation gateway check."
        )
    except Exception as e:
        # Check for rate limit error (429)
        error_str = str(e)
        if "429" in error_str or "rate_limit_exceeded" in error_str:
             raise HTTPException(status_code=429, detail="AI service quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")
