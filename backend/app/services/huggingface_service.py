import requests
import logging
import os
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class HuggingFaceImageService:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        # Using FLUX.1-schnell for fast, high-quality generation
        self.api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_image(self, prompt: str) -> Optional[bytes]:
        if not self.api_key:
            logger.error("HUGGINGFACE_API_KEY not set")
            return None
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt},
                timeout=30
            )
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"HuggingFace request failed: {e}")
            return None
