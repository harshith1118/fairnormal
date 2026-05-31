# FaithGuide AI

FaithGuide AI is an agentic, full-stack application engineered to provide accurate, contextually relevant religious data. Built with a robust FastAPI backend and a responsive Next.js/React frontend, the platform is designed around strict local validation layers to completely prevent AI hallucinations, handle API quota boundaries elegantly, and enforce rigid theological safety gates.

## System Architecture & Component Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Next.js, React.js, Tailwind CSS (`http://localhost:3000`) |
| **Backend** | Python, FastAPI, Uvicorn, SQLite (`http://localhost:8000`) |
| **Core AI** | Google GenAI SDK (Gemini 2.0/2.5 Flash, Imagen 4.0) |

## Key Engineering Features

*   **Denomination-Aware Context Selection:** By selecting a specific denomination (Protestant, Catholic, or Orthodox), the system dynamically alters vector search spaces to restrict theological data queries to the appropriate scripture canon (e.g., handling 66 vs 73 books correctly).
*   **Offline Verification Check:** A local Python structural validation layer intercepts out-of-bounds inputs—such as hallucinated chapter or verse references—and blocks them instantly before any cloud API calls are made.
*   **Safety Gateway Filter:** The backend employs a strict input evaluation engine. Prompts are run through an ALLOW/WARN/REFUSE matrix to proactively drop malicious injections or requests attempting to generate harmful interpretations.
*   **Three-Tier Hybrid Image Strategy:** A robust visual pipeline ensures consistent output:
    *   **Tier 1:** Attempts generation using Gemini Imagen.
    *   **Tier 2:** Falls back to a high-resolution Unsplash Sacred Art library upon hitting API quota ceilings.
    *   **Tier 3:** Triggers a local, stylized vector engine utilizing CSS filters and specular lighting maps to generate textures like stained glass or oil paintings.

## Automated Audit & Reproducibility

The system includes an integrated, 80-case evaluation suite persisted within the local SQLite database. By running `backend/scripts/verify_backend.py` or `backend/scripts/seed_db.py`, the system executes automated tests to track latency distributions, accuracy metrics, and image generation success rates, effectively removing the need for manual human QA.

## Quick Start & Local Deployment

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   A valid Google GenAI API Key

### Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
# Create a .env file and add your GEMINI_API_KEY
echo GEMINI_API_KEY=your_key_here > .env

# Start the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:3000`.
