from google import genai
from google.genai import types
import os
import base64
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Testing gemini-3.1-flash-image-preview via generate_content...")
try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents="Generate a high-quality oil painting of a biblical scene: Daniel in the lions den, majestic lighting, 1024x1024",
        config=types.GenerateContentConfig(
            temperature=0.7,
        )
    )
    
    print("Response received.")
    found_image = False
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            print(f"Found inline_data! MIME type: {part.inline_data.mime_type}")
            # print(f"Data snippet: {part.inline_data.data[:50]}...")
            found_image = True
        elif part.file_data:
            print(f"Found file_data! URI: {part.file_data.file_uri}")
            found_image = True
        elif part.text:
            print(f"Text part: {part.text[:100]}...")
            
    if not found_image:
        print("No image data found in the response parts.")
except Exception as e:
    print(f"Error: {e}")
