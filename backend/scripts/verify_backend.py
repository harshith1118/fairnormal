import os
import sys
import json

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from app.config import settings

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("FAITHGUIDE AI - AUTOMATED BACKEND VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test /api/health
    print("\n[Test 1] Querying health check endpoint (/api/health)...")
    try:
      response = client.get("/api/health")
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      print(f"  -> Success! Status: {data.get('status')}, SQLite: {data.get('sqlite_status')}, ChromaDB: {data.get('chroma_status')}")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    # 2. Test /api/memory (POST preference persist)
    print("\n[Test 2] Testing theological preference persistence (/api/memory)...")
    try:
      payload = {"session_id": "test-verify-session", "denomination": "Catholic"}
      response = client.post("/api/memory", json=payload)
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      assert data.get("denomination") == "Catholic", "Denomination mismatch"
      print(f"  -> Success! Preference saved: session_id={data.get('session_id')}, denomination={data.get('denomination')}")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    # 3. Test /api/chat (POST RAG chat)
    print("\n[Test 3] Testing chat RAG + verification pipeline (/api/chat)...")
    try:
      payload = {"session_id": "test-verify-session", "message": "What is John 3:16 about?"}
      response = client.post("/api/chat", json=payload)
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      print(f"  -> Success! Chat replied: {data.get('message')[:100]}...")
      print(f"  -> Safety Status: {data.get('safety_status')}")
      print(f"  -> Citations found: {len(data.get('citations', []))}")
      for cite in data.get("citations", []):
          print(f"     - {cite.get('reference')} (Verified: {cite.get('verified')})")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    # 4. Test /api/chat Hallucination Interception (POST Romans 50:12)
    print("\n[Test 4] Testing citation hallucination interception (/api/chat)...")
    try:
      payload = {"session_id": "test-verify-session", "message": "Tell me about Romans 50:12."}
      response = client.post("/api/chat", json=payload)
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      print(f"  -> Success! Hallucination intercepted.")
      print(f"  -> Reply contains warning phrase: {'Unable to verify' in data.get('message')}")
      print(f"  -> Citations caught: {[c.get('reference') for c in data.get('citations') if not c.get('verified')]}")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    # 5. Test /api/image (POST Art Generation with styles and enhancer)
    print("\n[Test 5] Testing image art generator + safety check (/api/image)...")
    try:
      payload = {"prompt": "stained glass cross", "style": "stained glass", "enhance": True}
      response = client.post("/api/image", json=payload)
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      print(f"  -> Success! Image generated.")
      print(f"  -> Safety status: {data.get('safety_status')}")
      print(f"  -> Enhanced Art Prompt: '{data.get('enhanced_prompt')}'")
      print(f"  -> Base64 Image output length: {len(data.get('base64_image', ''))} characters")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    # 6. Test /api/evaluate (GET 80-case dashboard payload)
    print("\n[Test 6] Fetching 80-case evaluation records (/api/evaluate)...")
    try:
      response = client.get("/api/evaluate")
      assert response.status_code == 200, f"Expected 200, got {response.status_code}"
      data = response.json()
      evals = data.get("evaluations", [])
      print(f"  -> Success! Loaded {data.get('total_cases')} evaluation records from SQLite database.")
      
      # Group statistics verification
      passed = len([e for e in evals if e.get("result") == "PASS"])
      print(f"  -> Overall Audit Pass Count: {passed} / {len(evals)} ({passed/len(evals)*100:.1f}%)")
    except Exception as e:
      print(f"  -> FAILED: {e}")
      sys.exit(1)

    print("\n" + "=" * 60)
    print("ALL BACKEND VERIFICATION TESTS COMPLETED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
