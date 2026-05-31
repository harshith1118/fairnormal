from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.database import get_history

router = APIRouter()

@router.get("/history")
async def get_history_endpoint(session_id: str = Query(..., description="The unique session ID to fetch history for")):
    history_logs = get_history(session_id)
    return {
        "session_id": session_id,
        "history": history_logs
    }
