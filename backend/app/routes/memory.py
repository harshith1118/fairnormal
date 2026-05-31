from fastapi import APIRouter
from app.models import PreferenceRequest, PreferenceResponse
from app.database import save_preference

router = APIRouter()

@router.post("/memory", response_model=PreferenceResponse)
async def update_preference(request: PreferenceRequest):
    save_preference(request.session_id, request.denomination)
    return PreferenceResponse(
        session_id=request.session_id,
        denomination=request.denomination,
        status="success"
    )
