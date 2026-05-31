from fastapi import APIRouter
from app.models import HealthResponse
from app.database import get_db_connection
from app.services.rag_service import RAGService

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    sqlite_status = "HEALTHY"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        sqlite_status = f"UNHEALTHY: {e}"
        
    chroma_status = "HEALTHY"
    try:
        collection = RAGService.get_collection()
        collection.count()
    except Exception as e:
        chroma_status = f"UNHEALTHY: {e}"
        
    status = "OK" if sqlite_status == "HEALTHY" and "UNHEALTHY" not in chroma_status else "DEGRADED"
    
    return HealthResponse(
        status=status,
        chroma_status=chroma_status,
        sqlite_status=sqlite_status
    )
