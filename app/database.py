import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 1,
        character_count INTEGER DEFAULT 0,
        word_count INTEGER DEFAULT 0,
        summary TEXT DEFAULT '',
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Document chunks table for RAG & Citation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        page_number INTEGER DEFAULT 1,
        text TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    """)

    # Flashcards table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        deck_title TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        difficulty TEXT DEFAULT 'medium',
        box INTEGER DEFAULT 1,
        reviews_count INTEGER DEFAULT 0,
        last_reviewed TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
    )
    """)

    # Quizzes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        title TEXT NOT NULL,
        difficulty TEXT DEFAULT 'medium',
        score REAL DEFAULT 0,
        total_questions INTEGER DEFAULT 5,
        questions_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
    )
    """)

    # Quiz attempts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id TEXT PRIMARY KEY,
        quiz_id TEXT NOT NULL,
        score REAL NOT NULL,
        total INTEGER NOT NULL,
        answers_json TEXT NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
    )
    """)

    # Chat messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        role TEXT NOT NULL,
        persona TEXT DEFAULT 'academic',
        content TEXT NOT NULL,
        citations_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Study sessions table (analytics and Pomodoro)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions (
        id TEXT PRIMARY KEY,
        session_type TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        notes TEXT DEFAULT '',
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# Database helper functions

def insert_document(doc: Dict[str, Any], chunks: List[Dict[str, Any]]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (id, filename, file_type, file_size, page_count, character_count, word_count, summary, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc['id'], doc['filename'], doc['file_type'], doc['file_size'],
        doc['page_count'], doc['character_count'], doc['word_count'],
        doc.get('summary', ''), doc['content'], doc.get('created_at', datetime.utcnow().isoformat())
    ))

    for chunk in chunks:
        cursor.execute("""
            INSERT INTO document_chunks (document_id, chunk_index, page_number, text)
            VALUES (?, ?, ?, ?)
        """, (doc['id'], chunk['chunk_index'], chunk['page_number'], chunk['text']))

    conn.commit()
    conn.close()
    return doc['id']

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, file_type, file_size, page_count, character_count, word_count, summary, created_at FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    docs = [dict(row) for row in rows]
    conn.close()
    return docs

def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_document(doc_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM document_chunks WHERE document_id = ?", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    return True

def get_document_chunks(doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if doc_id:
        cursor.execute("SELECT id, document_id, chunk_index, page_number, text FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC", (doc_id,))
    else:
        cursor.execute("SELECT id, document_id, chunk_index, page_number, text FROM document_chunks ORDER BY id ASC")
    rows = cursor.fetchall()
    chunks = [dict(row) for row in rows]
    conn.close()
    return chunks

def save_flashcards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    saved = []
    for c in cards:
        card_id = c.get('id', str(uuid.uuid4()))
        cursor.execute("""
            INSERT INTO flashcards (id, document_id, deck_title, front, back, difficulty, box, reviews_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            card_id, c.get('document_id'), c.get('deck_title', 'General'),
            c['front'], c['back'], c.get('difficulty', 'medium'),
            c.get('box', 1), c.get('reviews_count', 0), datetime.utcnow().isoformat()
        ))
        c['id'] = card_id
        saved.append(c)
    conn.commit()
    conn.close()
    return saved

def get_flashcards(deck_title: Optional[str] = None, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM flashcards WHERE 1=1"
    params = []
    if deck_title and deck_title != "all":
        query += " AND deck_title = ?"
        params.append(deck_title)
    if document_id:
        query += " AND document_id = ?"
        params.append(document_id)
    query += " ORDER BY box ASC, created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cards = [dict(row) for row in rows]
    conn.close()
    return cards

def update_flashcard_review(card_id: str, rating: str):
    """
    Spaced repetition (Leitner Box update):
    - easy: box + 1 (max 5)
    - good: box stays or +1 if box 1
    - hard: box resets to 1
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT box, reviews_count FROM flashcards WHERE id = ?", (card_id,))
    row = cursor.fetchone()
    if row:
        curr_box = row['box']
        curr_count = row['reviews_count']
        if rating == 'easy':
            new_box = min(5, curr_box + 1)
        elif rating == 'good':
            new_box = min(5, max(1, curr_box if curr_box > 1 else 2))
        else:  # hard
            new_box = 1
        
        cursor.execute("""
            UPDATE flashcards 
            SET box = ?, reviews_count = ?, last_reviewed = ?
            WHERE id = ?
        """, (new_box, curr_count + 1, datetime.utcnow().isoformat(), card_id))
        conn.commit()
    conn.close()

def delete_flashcard(card_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()

def save_quiz(quiz_data: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    quiz_id = quiz_data.get('id', str(uuid.uuid4()))
    cursor.execute("""
        INSERT INTO quizzes (id, document_id, title, difficulty, score, total_questions, questions_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        quiz_id, quiz_data.get('document_id'), quiz_data['title'],
        quiz_data.get('difficulty', 'medium'), quiz_data.get('score', 0),
        quiz_data.get('total_questions', len(quiz_data['questions'])),
        json.dumps(quiz_data['questions']), datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return quiz_id

def get_quizzes() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    quizzes = []
    for row in rows:
        item = dict(row)
        try:
            item['questions'] = json.loads(item['questions_json'])
        except Exception:
            item['questions'] = []
        quizzes.append(item)
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    item = dict(row)
    item['questions'] = json.loads(item['questions_json'])
    conn.close()
    return item

def record_quiz_attempt(quiz_id: str, score: float, total: int, answers: List[Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    attempt_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO quiz_attempts (id, quiz_id, score, total, answers_json, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (attempt_id, quiz_id, score, total, json.dumps(answers), datetime.utcnow().isoformat()))
    
    # Update latest score on quiz
    cursor.execute("UPDATE quizzes SET score = ? WHERE id = ?", (score, quiz_id))
    conn.commit()
    conn.close()
    return attempt_id

def save_chat_message(msg: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    msg_id = msg.get('id', str(uuid.uuid4()))
    cursor.execute("""
        INSERT INTO chat_messages (id, document_id, role, persona, content, citations_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        msg_id, msg.get('document_id'), msg['role'], msg.get('persona', 'academic'),
        msg['content'], json.dumps(msg.get('citations', [])), datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return msg_id

def get_chat_history(document_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if document_id:
        cursor.execute("SELECT * FROM chat_messages WHERE document_id = ? ORDER BY created_at ASC LIMIT ?", (document_id, limit))
    else:
        cursor.execute("SELECT * FROM chat_messages ORDER BY created_at ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    messages = []
    for r in rows:
        d = dict(r)
        try:
            d['citations'] = json.loads(d['citations_json'])
        except Exception:
            d['citations'] = []
        messages.append(d)
    conn.close()
    return messages

def clear_chat_history(document_id: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if document_id:
        cursor.execute("DELETE FROM chat_messages WHERE document_id = ?", (document_id,))
    else:
        cursor.execute("DELETE FROM chat_messages")
    conn.commit()
    conn.close()

def record_study_session(session_type: str, duration_seconds: int, notes: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO study_sessions (id, session_type, duration_seconds, notes, completed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), session_type, duration_seconds, notes, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_analytics_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM documents")
    total_docs = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count, SUM(reviews_count) as reviews FROM flashcards")
    fc_row = cursor.fetchone()
    total_flashcards = fc_row['count']
    total_reviews = fc_row['reviews'] or 0

    cursor.execute("SELECT COUNT(*) as mastered FROM flashcards WHERE box >= 4")
    mastered_cards = cursor.fetchone()['mastered']

    cursor.execute("SELECT COUNT(*) as total_quizzes, AVG(score) as avg_score FROM quiz_attempts")
    qa_row = cursor.fetchone()
    total_quizzes_taken = qa_row['total_quizzes']
    avg_quiz_score = round(qa_row['avg_score'] or 0.0, 1)

    cursor.execute("SELECT SUM(duration_seconds) as total_study_time FROM study_sessions")
    total_study_seconds = cursor.fetchone()['total_study_time'] or 0

    # Recent study history by day (last 7 days)
    cursor.execute("""
        SELECT date(completed_at) as study_date, SUM(duration_seconds) as total_seconds
        FROM study_sessions
        GROUP BY date(completed_at)
        ORDER BY study_date DESC
        LIMIT 7
    """)
    recent_activity = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_documents": total_docs,
        "total_flashcards": total_flashcards,
        "total_reviews": total_reviews,
        "mastered_flashcards": mastered_cards,
        "total_quizzes_taken": total_quizzes_taken,
        "average_quiz_score": avg_quiz_score,
        "total_study_minutes": round(total_study_seconds / 60, 1),
        "recent_activity": recent_activity
    }

