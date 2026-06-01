# FaithGuide AI

FaithGuide AI is an agentic, full-stack application engineered to provide accurate, contextually relevant religious data. Built with a robust FastAPI backend and a responsive Next.js/React frontend, the platform is designed around strict local validation layers to completely prevent AI hallucinations and enforce rigid theological safety gates.

## 🚀 Live Application
*   **Production App:** [https://faithguide-frontend-692034349177.us-central1.run.app](https://faithguide-frontend-692034349177.us-central1.run.app)
*   **Theological API:** [https://faithguide-backend-692034349177.us-central1.run.app/docs](https://faithguide-backend-692034349177.us-central1.run.app/docs)

## System Architecture & Component Stack

| Component | Technology | Deployment |
| :--- | :--- | :--- |
| **Frontend** | Next.js, React.js, Tailwind CSS | Google Cloud Run |
| **Backend** | Python, FastAPI, Uvicorn, SQLite | Google Cloud Run |
| **Database** | SQLite + ChromaDB (Vector) | GCS FUSE Persistence |
| **Core AI** | Google Gemini (2.0/2.5 Flash), Groq (Llama 3), HF | Serverless API |

## Key Engineering Features

*   **Denomination-Aware Context Selection:** By selecting a specific denomination (Protestant, Catholic, or Orthodox), the system dynamically alters vector search spaces to restrict theological data queries to the appropriate scripture canon.
*   **Persistence via GCS FUSE:** Although running on serverless infrastructure (Cloud Run), the backend maintains state (chat history and vector embeddings) by mounting a Google Cloud Storage bucket as a local file system.
*   **Safety Gateway Filter:** The backend employs a strict input evaluation engine. Prompts are run through an ALLOW/WARN/REFUSE matrix to proactively drop malicious injections.
*   **Scalable CI/CD:** Orchestrated via Google Cloud Build with automated Docker containerization and deployment to us-central1.

## Automated Audit & Reproducibility

The system includes an integrated, 80-case evaluation suite. In production, this can be triggered via the UI to track latency distributions, accuracy metrics, and image generation success rates against baseline theological PASS results.

## Local Development

### Prerequisites
*   Python 3.11+
*   Node.js 22+
*   GCP CLI (for cloud deployments)

### Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv, then:
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps
# Point to your local or deployed backend
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
npm run dev
```

## 🛠 Recent Updates
*   **GCP Deployment:** Added `cloudbuild.yaml`, `.gcloudignore`, and optimized Dockerfiles for Google Cloud Run.
*   **Architecture Documentation:** Created `ARCHITECTURE.md` to document the system's high-level design and data flow.
*   **Backend Enhancements:** 
    - Switched to dynamic `$PORT` for Cloud Run compatibility.
    - Updated CORS to allow all origins for production flexibility.
    - Integrated `groq` and `tenacity` for better LLM performance and reliability.
*   **Frontend Improvements:**
    - Implemented request timeouts and abort controllers in the API layer.
    - Added build-time environment variable support for API URLs.
