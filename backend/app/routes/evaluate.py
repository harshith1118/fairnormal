from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from app.models import EvalRunRequest
from app.database import get_evaluations, clear_evaluations, set_status, get_status
from app.services.eval_service import EvalService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/evaluate")
async def get_evaluations_endpoint():
    try:
        records = get_evaluations()
        running = get_status("eval_running") == "True"
        progress = get_status("eval_progress")
        return {
            "total_cases": len(records),
            "evaluations": records,
            "running": running,
            "progress": int(progress) if progress.isdigit() else 0
        }
    except Exception as e:
        logger.error(f"Error fetching evaluations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch evaluations: {e}")

@router.post("/evaluate")
async def run_evaluations_endpoint(background_tasks: BackgroundTasks, request: Optional[EvalRunRequest] = None):
    if get_status("eval_running") == "True":
        raise HTTPException(status_code=400, detail="Evaluation already running")

    subset = request.test_id_subset if request else None

    def run_task():
        logger.info("Background evaluation task started.")
        set_status("eval_running", "True")
        set_status("eval_progress", "0")
        try:
            # Clear previous results before starting
            clear_evaluations()
            import asyncio
            asyncio.run(EvalService.run_evaluations(subset_ids=subset))
            logger.info("Background evaluation task finished successfully.")
        except Exception as e:
            logger.error(f"Background task failed: {e}")
        finally:
            set_status("eval_running", "False")
            set_status("eval_progress", "100")
            logger.info("Background evaluation task finally block executed.")

    background_tasks.add_task(run_task)
    return {
        "status": "accepted",
        "message": "Evaluation run started in background."
    }
