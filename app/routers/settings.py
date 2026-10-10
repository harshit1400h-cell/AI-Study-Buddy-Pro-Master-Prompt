from fastapi import APIRouter
from app.config import settings, save_settings
from app.models import SettingsUpdateRequest, VerifyKeyRequest
from app.ai_service import AIService

router = APIRouter(prefix="/api/settings", tags=["settings"])

def mask_key(k: str) -> str:
    if not k or len(k) < 8:
        return "" if not k else "••••••••"
    return k[:4] + "••••••••" + k[-4:]

@router.get("")
def get_current_settings():
    return {
        "provider": settings.provider,
        "gemini_api_key_masked": mask_key(settings.gemini_api_key),
        "has_gemini_key": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "openai_api_key_masked": mask_key(settings.openai_api_key),
        "has_openai_key": bool(settings.openai_api_key),
        "openai_model": settings.openai_model,
        "active_provider_label": AIService.get_active_provider()
    }

@router.post("")
def update_settings(payload: SettingsUpdateRequest):
    settings.provider = payload.provider
    if payload.gemini_api_key is not None and payload.gemini_api_key.strip():
        settings.gemini_api_key = payload.gemini_api_key.strip()
    if payload.gemini_model:
        settings.gemini_model = payload.gemini_model
    if payload.openai_api_key is not None and payload.openai_api_key.strip():
        settings.openai_api_key = payload.openai_api_key.strip()
    if payload.openai_model:
        settings.openai_model = payload.openai_model

    save_settings(settings)
    return {"status": "success", "message": "Settings updated successfully"}

@router.post("/verify")
async def verify_key(payload: VerifyKeyRequest):
    result = await AIService.verify_api_key(payload.provider, payload.api_key)
    return result

