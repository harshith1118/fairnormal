import os
from dotenv import load_dotenv
import requests

# Load env manually to verify
load_dotenv(dotenv_path="backend/.env")
key = os.getenv("HUGGINGFACE_API_KEY")
print(f"Key loaded: {key[:6]}..." if key else "Key NOT loaded")

if key:
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": "A simple cross on a hill"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
