from fastapi import APIRouter
from app.models import StudySessionLogRequest
from app.database import get_analytics_summary, record_study_session

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("")
def get_analytics():
    return get_analytics_summary()

@router.post("/session")
def log_session(payload: StudySessionLogRequest):
    record_study_session(
        session_type=payload.session_type,
        duration_seconds=payload.duration_seconds,
        notes=payload.notes or ""
    )
    return {"status": "success", "message": "Study session logged"}

