from fastapi import APIRouter, HTTPException
from app.models import QuizGenerateRequest, QuizSubmitRequest
from app.ai_service import AIService
from app.database import (
    save_quiz, get_quizzes, get_quiz_by_id, record_quiz_attempt, 
    get_document_by_id, get_all_documents, record_study_session
)

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])

@router.get("")
def list_quizzes():
    return get_quizzes()

@router.get("/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/generate")
async def generate_quiz(payload: QuizGenerateRequest):
    text_content = ""
    title = payload.title or "Knowledge Assessment"

    if payload.document_id:
        doc = get_document_by_id(payload.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        text_content = doc["content"]
        if payload.title == "Knowledge Assessment":
            title = f"{doc['filename'].replace('.pdf','').replace('.txt','')} Quiz"
    else:
        docs = get_all_documents()
        if docs:
            doc = get_document_by_id(docs[0]["id"])
            text_content = doc["content"]
            title = f"{doc['filename'].replace('.pdf','').replace('.txt','')} Quiz"
        else:
            raise HTTPException(status_code=400, detail="Please upload a document or load sample materials first")

    quiz_data = await AIService.generate_quiz(
        document_text=text_content,
        title=title,
        num_questions=payload.num_questions,
        difficulty=payload.difficulty
    )

    quiz_data["document_id"] = payload.document_id
    quiz_id = save_quiz(quiz_data)
    quiz_data["id"] = quiz_id

    return {"status": "success", "quiz": quiz_data}

@router.post("/submit")
def submit_quiz_answers(payload: QuizSubmitRequest):
    quiz = get_quiz_by_id(payload.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = quiz.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    # Map student answers
    student_answers_map = {}
    for a in payload.answers:
        student_answers_map[a.get("question_id")] = a.get("selected_option")

    correct_count = 0
    graded_questions = []

    for idx, q in enumerate(questions):
        q_id = q.get("id", idx + 1)
        user_choice = student_answers_map.get(q_id, "")
        correct_choice = q.get("correct_answer", "")
        
        is_correct = (user_choice.strip().lower() == correct_choice.strip().lower())
        if is_correct:
            correct_count += 1

        graded_questions.append({
            "id": q_id,
            "question": q.get("question"),
            "options": q.get("options", []),
            "user_choice": user_choice,
            "correct_choice": correct_choice,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    total = len(questions)
    percentage = round((correct_count / total) * 100, 1)

    attempt_id = record_quiz_attempt(
        quiz_id=payload.quiz_id,
        score=percentage,
        total=total,
        answers=graded_questions
    )

    # Log study session duration (approx 60s per question)
    record_study_session("quiz", total * 60, f"Completed quiz '{quiz['title']}' with score {percentage}%")

    return {
        "status": "success",
        "attempt_id": attempt_id,
        "score": percentage,
        "correct_count": correct_count,
        "total_questions": total,
        "graded_questions": graded_questions
    }

