from fastapi import APIRouter, HTTPException
from app.models import ChatRequest
from app.rag_engine import SimpleRAGSearcher
from app.ai_service import AIService
from app.database import (
    save_chat_message, get_chat_history, clear_chat_history, get_document_by_id
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/history")
def get_history(document_id: str = None):
    return get_chat_history(document_id=document_id)

@router.delete("/clear")
def clear_history(document_id: str = None):
    clear_chat_history(document_id=document_id)
    return {"status": "success", "message": "Chat history cleared"}

@router.post("/send")
async def send_chat_message(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 1. Retrieve RAG chunks
    context_chunks = SimpleRAGSearcher.search(
        query=payload.message,
        document_id=payload.document_id,
        top_k=4
    )

    # 2. Get recent conversational context
    history = get_chat_history(document_id=payload.document_id, limit=6)

    # 3. Save user message
    user_msg_id = save_chat_message({
        "document_id": payload.document_id,
        "role": "user",
        "persona": payload.persona,
        "content": payload.message,
        "citations": []
    })

    # 4. Generate AI response
    ai_result = await AIService.chat(
        message=payload.message,
        context_chunks=context_chunks,
        persona=payload.persona,
        history=history
    )

    # 5. Save assistant reply
    assistant_msg_id = save_chat_message({
        "document_id": payload.document_id,
        "role": "assistant",
        "persona": payload.persona,
        "content": ai_result["reply"],
        "citations": ai_result.get("citations", [])
    })

    return {
        "status": "success",
        "reply": ai_result["reply"],
        "citations": ai_result.get("citations", []),
        "provider": ai_result.get("provider", "AI Study Buddy"),
        "user_message_id": user_msg_id,
        "assistant_message_id": assistant_msg_id
    }

