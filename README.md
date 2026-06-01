# 🕊️ FaithGuide AI
### *Agentic Theological Intelligence & Scripture-Grounded Synthesis*

[![Live Demo](https://img.shields.io/badge/Live-Production_App-blue?style=for-the-badge&logo=googlecloud)](https://faithguide-frontend-692034349177.us-central1.run.app)
[![API Docs](https://img.shields.io/badge/API-Swagger_UI-green?style=for-the-badge&logo=fastapi)](https://faithguide-backend-692034349177.us-central1.run.app/docs)

FaithGuide AI is a sophisticated, agentic full-stack platform designed to provide accurate, contextually aware religious data. Unlike generic LLMs, FaithGuide AI employs a **multi-layered verification architecture** to eliminate hallucinations, enforce theological safety, and respect denominational boundaries.

---

## ✨ Key Capabilities

*   **🛡️ Hallucination-Proof RAG:** Utilizes a custom Vector Store (ChromaDB) to ground every response in verified scripture and theological texts.
*   **⛪ Denominational Intelligence:** Dynamically adjusts its knowledge base and search space based on the user's tradition (Protestant, Catholic, or Orthodox), ensuring canon-accurate references (e.g., handling the Deuterocanon correctly).
*   **⚖️ Theological Safety Gateway:** A proprietary "Allow/Warn/Refuse" matrix that filters prompts and generations to maintain a respectful, safe, and doctrinally sound environment.
*   **🖼️ Sacred Art Engine:** A multi-tier image generation pipeline that transitions from Gemini Imagen to curated sacred art libraries, ensuring visual quality even under high load.
*   **🚀 Cloud-Native Persistence:** Leverages Google Cloud Storage FUSE to maintain long-term memory and vector state on serverless infrastructure.

---

## 🛠️ The Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Next.js 15, React, Tailwind CSS | Responsive, accessible, and fast user interface. |
| **Backend** | Python 3.11, FastAPI, Groq | High-performance asynchronous API & LLM orchestration. |
| **Intelligence** | Gemini 2.0 Flash, Llama 3 (Groq) | State-of-the-art reasoning and synthesis. |
| **Memory** | ChromaDB (Vector) + SQLite | Persistent history and semantic retrieval. |
| **DevOps** | Docker, Google Cloud Run, GCB | Scalable, containerized deployment pipeline. |

---

## 🏗️ Architecture at a Glance

The system is built on a **Service-Oriented Architecture (SOA)**, ensuring that safety, retrieval, and generation are decoupled and independently scalable.

> [!TIP]
> For a deep dive into our technical design, check out [**ARCHITECTURE.md**](./ARCHITECTURE.md).

---

## 🚀 Getting Started

### Prerequisites
- Node.js 22+ & Python 3.11+
- Google Cloud CLI (optional, for deployment)
- API Keys for Google Gemini & Groq

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
npm run dev
```

---

## 🧪 Quality & Validation

FaithGuide AI includes a **Continuous Evaluation Suite** with over 80 theological test cases. This suite tracks:
- **Latency Distribution:** Ensuring responses are fast and reliable.
- **Accuracy Metrics:** Measuring RAG retrieval precision.
- **Safety Compliance:** Verifying that the Safety Gateway correctly identifies and blocks out-of-bounds content.

---

## 📈 Recent Engineering Milestones

- ✅ **Serverless Persistence:** Successfully implemented GCS FUSE mounting for stateless containers.
- ✅ **Parallel Verification:** Reduced citation validation time by 60% using async parallel processing.
- ✅ **Universal CORS:** Optimized for cross-origin production environments.
- ✅ **Dynamic Environment Injection:** Seamless transition between local development and Cloud Run production.

---

## 📜 License & Acknowledgments
Built with a commitment to theological accuracy and technical excellence. Special thanks to the open-source communities behind FastAPI, Next.js, and ChromaDB.
