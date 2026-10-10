import json
from fastapi import APIRouter, HTTPException
from app.models import SummaryGenerateRequest
from app.ai_service import AIService
from app.database import get_document_by_id, get_db_connection

router = APIRouter(prefix="/api/summaries", tags=["summaries"])

@router.post("/generate")
async def generate_summary(payload: SummaryGenerateRequest):
    doc = get_document_by_id(payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await AIService.generate_summary(
        document_text=doc["content"],
        document_title=doc["filename"]
    )

    # Save summary snippet in documents table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET summary = ? WHERE id = ?", (result.get("tldr", ""), payload.document_id))
    conn.commit()
    conn.close()

    return {"status": "success", "summary": result}

@router.get("/{doc_id}")
async def get_summary(doc_id: str):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await AIService.generate_summary(
        document_text=doc["content"],
        document_title=doc["filename"]
    )
    return {"status": "success", "summary": result}

