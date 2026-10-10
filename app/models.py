from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class SettingsUpdateRequest(BaseModel):
    provider: str = Field(..., description="Provider name: 'smart_local', 'gemini', or 'openai'")
    gemini_api_key: Optional[str] = ""
    gemini_model: Optional[str] = "gemini-1.5-flash"
    openai_api_key: Optional[str] = ""
    openai_model: Optional[str] = "gpt-4o-mini"

class VerifyKeyRequest(BaseModel):
    provider: str
    api_key: str

class ChatRequest(BaseModel):
    message: str
    document_id: Optional[str] = None
    persona: str = Field("academic", description="'academic', 'socratic', 'simplifier', or 'exam_coach'")

class QuizGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    title: Optional[str] = "Knowledge Assessment"
    num_questions: int = Field(5, ge=1, le=20)
    difficulty: str = Field("medium", description="'easy', 'medium', or 'hard'")

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: List[Dict[str, Any]]  # [{"question_id": 1, "selected_option": "..."}]

class FlashcardGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    deck_title: Optional[str] = "General Review"
    count: int = Field(8, ge=2, le=30)

class FlashcardReviewRequest(BaseModel):
    card_id: str
    rating: str = Field(..., description="'easy', 'good', or 'hard'")

class SummaryGenerateRequest(BaseModel):
    document_id: str

class StudySessionLogRequest(BaseModel):
    session_type: str  # 'pomodoro', 'flashcard_review', 'quiz', 'chat'
    duration_seconds: int
    notes: Optional[str] = ""

class TextUploadRequest(BaseModel):
    title: str
    content: str

