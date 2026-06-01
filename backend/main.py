import os
from dotenv import load_dotenv
load_dotenv()
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.services.eval_service import EvalService
from app.routes import chat, image, memory, history, health, evaluate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FaithGuide AI secure theological backend layer managing sessions, prompt safety shields, and scripture verification."
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing FaithGuide AI database schema...")
    
    # Check if database exists
    db_file = settings.DATABASE_PATH
    db_exists = os.path.exists(db_file)
    
    # Run schema setup
    init_db()
    
    # If the database was just created, seed baseline evaluations
    if not db_exists:
        logger.info("New database detected. Seeding baseline evaluation datasets...")
        try:
            EvalService.seed_pre_evaluated_results()
            logger.info("Baseline evaluations successfully pre-seeded.")
        except Exception as e:
            logger.error(f"Failed to auto-seed baseline evaluations: {e}")

# Register route modules
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(image.router, prefix="/api", tags=["image"])
app.include_router(memory.router, prefix="/api", tags=["memory"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(evaluate.router, prefix="/api", tags=["evaluate"])

@app.get("/")
def read_root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
