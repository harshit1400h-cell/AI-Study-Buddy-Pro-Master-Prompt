from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models import FlashcardGenerateRequest, FlashcardReviewRequest
from app.ai_service import AIService
from app.database import (
    save_flashcards, get_flashcards, update_flashcard_review, 
    delete_flashcard, get_document_by_id, record_study_session
)

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])

@router.get("")
def list_flashcards(deck_title: Optional[str] = None, document_id: Optional[str] = None):
    return get_flashcards(deck_title=deck_title, document_id=document_id)

@router.post("/generate")
async def generate_cards(payload: FlashcardGenerateRequest):
    text_content = ""
    deck_name = payload.deck_title or "General"

    if payload.document_id:
        doc = get_document_by_id(payload.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        text_content = doc["content"]
        if not payload.deck_title:
            deck_name = doc["filename"].replace(".pdf", "").replace(".txt", "")
    else:
        # Pull latest document if none specified
        from app.database import get_all_documents
        docs = get_all_documents()
        if docs:
            doc = get_document_by_id(docs[0]["id"])
            text_content = doc["content"]
            deck_name = doc["filename"].replace(".pdf", "").replace(".txt", "")
        else:
            raise HTTPException(status_code=400, detail="Please upload a document or load sample materials first")

    generated = await AIService.generate_flashcards(
        document_text=text_content,
        deck_title=deck_name,
        count=payload.count
    )

    for c in generated:
        c["document_id"] = payload.document_id

    saved = save_flashcards(generated)
    return {"status": "success", "count": len(saved), "cards": saved}

@router.post("/review")
def review_card(payload: FlashcardReviewRequest):
    if payload.rating not in ["easy", "good", "hard"]:
        raise HTTPException(status_code=400, detail="Rating must be 'easy', 'good', or 'hard'")
    update_flashcard_review(payload.card_id, payload.rating)
    # Log 30 seconds study session per card
    record_study_session("flashcard_review", 30, f"Card review rating: {payload.rating}")
    return {"status": "success", "message": f"Card updated with rating '{payload.rating}'"}

@router.delete("/{card_id}")
def remove_card(card_id: str):
    delete_flashcard(card_id)
    return {"status": "success", "message": "Card deleted"}

