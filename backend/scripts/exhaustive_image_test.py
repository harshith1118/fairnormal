from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# We will try every model that looks like it could generate an image or high-end content
candidate_models = [
    "imagen-4.0-generate-001",
    "imagen-3.0-generate-002",
    "veo-3.1-lite-generate-preview",
    "veo-3.0-fast-generate-001",
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "antigravity-preview-05-2026"
]

for model in candidate_models:
    print(f"--- Testing {model} ---")
    try:
        if "imagen" in model or "veo" in model:
            # Try generate_images for Imagen/Veo
            result = client.models.generate_images(
                model=model,
                prompt="A beautiful oil painting of a cross on a hill at sunset, sacred atmosphere",
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            print(f"  SUCCESS (generate_images) with {model}")
            # print(result)
            break
        else:
            # Try generate_content for Gemini-image/Antigravity
            response = client.models.generate_content(
                model=model,
                contents="Generate an image of a cross on a hill.",
            )
            print(f"  SUCCESS (generate_content) with {model}")
            # Check for parts
            found = False
            for part in response.candidates[0].content.parts:
                if part.inline_data or part.file_data:
                    found = True
            if found:
                print(f"  IMAGE DATA FOUND in {model}!")
                break
            else:
                print(f"  No image data in response from {model}")
    except Exception as e:
        print(f"  FAILED with {model}: {e}")
