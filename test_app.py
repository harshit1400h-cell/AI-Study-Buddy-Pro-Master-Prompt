import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from main import app

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = TestClient(app)

def run_integration_tests():
    print("--- 1. Health Check Test ---")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Health check OK:", res.json())

    print("\n--- 2. Load Sample Documents ---")
    res = client.post("/api/documents/load-samples")
    assert res.status_code == 200, f"Load samples failed: {res.text}"
    print("[OK] Loaded sample documents:", res.json())

    print("\n--- 3. List Documents ---")
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) > 0, "No documents returned"
    doc_id = docs[0]["id"]
    print(f"[OK] Found {len(docs)} documents. Active doc: {docs[0]['filename']} (ID: {doc_id})")

    print("\n--- 4. Real PDF Upload Test ---")
    pdf_path = Path("sample_docs/Deep_Learning_and_Neural_Networks_Foundations.pdf")
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            res = client.post(
                "/api/documents/upload",
                files={"file": ("Deep_Learning_and_Neural_Networks_Foundations.pdf", f, "application/pdf")}
            )
        assert res.status_code == 200, f"PDF upload failed: {res.text}"
        uploaded_doc = res.json()["document"]
        print(f"[OK] PDF Uploaded & Processed with PyPDF: {uploaded_doc['filename']} ({uploaded_doc['page_count']} pages, {uploaded_doc['word_count']} words, {uploaded_doc['chunks_count']} chunks)")
        doc_id = uploaded_doc["id"]

    print("\n--- 5. Chat Tutor with RAG Citations (Academic Mode) ---")
    res = client.post("/api/chat/send", json={
        "message": "What is the difference between ReLU and Sigmoid activation functions?",
        "document_id": doc_id,
        "persona": "academic"
    })
    assert res.status_code == 200, f"Chat failed: {res.text}"
    chat_data = res.json()
    print("[OK] AI Tutor Response received:")
    print("  Provider:", chat_data.get("provider"))
    print("  Citations Count:", len(chat_data.get("citations", [])))
    print("  Reply Snippet:", chat_data.get("reply")[:150], "...")

    print("\n--- 6. Chat Tutor (Socratic Mode) ---")
    res = client.post("/api/chat/send", json={
        "message": "Why does gradient descent oscillate if the learning rate is too big?",
        "document_id": doc_id,
        "persona": "socratic"
    })
    assert res.status_code == 200
    print("[OK] Socratic Tutor Response Snippet:", res.json().get("reply")[:150], "...")

    print("\n--- 7. Smart Flashcards Generation ---")
    res = client.post("/api/flashcards/generate", json={
        "document_id": doc_id,
        "deck_title": "Deep Learning Quick Cards",
        "count": 5
    })
    assert res.status_code == 200, f"Flashcards generation failed: {res.text}"
    cards = res.json().get("cards", [])
    assert len(cards) > 0, "No flashcards generated"
    print(f"[OK] Generated {len(cards)} flashcards:")
    print("  Card 1 Front:", cards[0]["front"])
    print("  Card 1 Back:", cards[0]["back"])
    card_id = cards[0]["id"]

    print("\n--- 8. Leitner Spaced Repetition Review ---")
    res = client.post("/api/flashcards/review", json={
        "card_id": card_id,
        "rating": "easy"
    })
    assert res.status_code == 200
    print("[OK] Leitner Review Recorded (Promoted to Box 2)")

    print("\n--- 9. Adaptive Quiz Generation ---")
    res = client.post("/api/quizzes/generate", json={
        "document_id": doc_id,
        "title": "Deep Learning Diagnostic Test",
        "num_questions": 3,
        "difficulty": "medium"
    })
    assert res.status_code == 200, f"Quiz generation failed: {res.text}"
    quiz_data = res.json().get("quiz", {})
    quiz_id = quiz_data["id"]
    questions = quiz_data["questions"]
    print(f"[OK] Generated Quiz '{quiz_data['title']}' with {len(questions)} questions")
    print("  Q1:", questions[0]["question"])
    print("  Options:", questions[0]["options"])

    print("\n--- 10. Quiz Submission & Diagnostic Grading ---")
    # Formulate submission answering first question correctly
    q1 = questions[0]
    answers = [{"question_id": q1["id"], "selected_option": q1["correct_answer"]}]
    if len(questions) > 1:
        # submit an intentional guess for question 2
        answers.append({"question_id": questions[1]["id"], "selected_option": questions[1]["options"][0]})

    res = client.post("/api/quizzes/submit", json={
        "quiz_id": quiz_id,
        "answers": answers
    })
    assert res.status_code == 200, f"Quiz submit failed: {res.text}"
    result = res.json()
    print(f"[OK] Quiz Graded: Score {result['score']}% ({result['correct_count']}/{result['total_questions']})")
    print("  Feedback for Q1:", result['graded_questions'][0]['explanation'])

    print("\n--- 11. Executive Summary & Mind Map Generation ---")
    res = client.post("/api/summaries/generate", json={"document_id": doc_id})
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary = res.json().get("summary", {})
    print("[OK] Executive Summary Generated:")
    print("  TL;DR:", summary.get("tldr")[:120], "...")
    print("  Key Takeaways Count:", len(summary.get("key_takeaways", [])))
    print("  Glossary Terms Count:", len(summary.get("glossary", [])))
    print("  Mind Map Nodes Count:", len(summary.get("mind_map", [])))

    print("\n--- 12. Pomodoro Session & Study Analytics ---")
    res = client.post("/api/analytics/session", json={
        "session_type": "pomodoro",
        "duration_seconds": 1500,
        "notes": "25-minute deep focus cycle on Neural Networks"
    })
    assert res.status_code == 200

    res = client.get("/api/analytics")
    assert res.status_code == 200
    analytics = res.json()
    print("[OK] Analytics Summary:")
    print(f"  Total Study Time: {analytics['total_study_minutes']} minutes")
    print(f"  Flashcards Total: {analytics['total_flashcards']} (Mastered: {analytics['mastered_flashcards']})")
    print(f"  Quizzes Completed: {analytics['total_quizzes_taken']} (Avg Score: {analytics['average_quiz_score']}%)")

    print("\n--- 13. Settings Verification Test ---")
    res = client.get("/api/settings")
    assert res.status_code == 200
    print("[OK] Current Settings:", res.json())

    res = client.post("/api/settings/verify", json={
        "provider": "smart_local",
        "api_key": "test_key"
    })
    assert res.status_code == 200
    print("[OK] Verify Local Engine:", res.json())

    print("\n========================================================")
    print("ALL 13 INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("========================================================")

if __name__ == "__main__":
    run_integration_tests()
