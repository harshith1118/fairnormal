from google import genai
from google.genai import types
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Checking gemini-2.0-flash tools...")
try:
    # Check if the model supports image generation as a tool
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Generate an oil painting of a cross on a hill.",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())], # Just testing tool capability
        )
    )
    print("Model response received. Checking for tool calls or specific outputs...")
    # print(response)
except Exception as e:
    print(f"Tool check failed: {e}")

print("\nAttempting direct REST call for Imagen 4.0 Standard...")
url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
headers = {"Content-Type": "application/json"}
data = {
    "instances": [{"prompt": "A beautiful oil painting of a cross on a hill"}],
    "parameters": {"sampleCount": 1}
}

try:
    res = requests.post(url, headers=headers, json=data)
    print(f"REST Status: {res.status_code}")
    print(f"REST Response: {res.text[:500]}")
except Exception as e:
    print(f"REST Call failed: {e}")
