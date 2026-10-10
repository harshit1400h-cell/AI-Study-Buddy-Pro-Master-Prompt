import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.config import UPLOADS_DIR, settings
from app.database import (
    insert_document, get_all_documents, get_document_by_id, 
    delete_document, get_document_chunks
)
from app.pdf_processor import (
    extract_text_from_pdf, extract_text_from_txt, 
    chunk_text, get_text_metrics, clean_text
)
from app.sample_data import SAMPLE_TOPICS
from app.models import TextUploadRequest

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("")
def list_documents():
    return get_all_documents()

@router.get("/{doc_id}")
def get_document(doc_id: str):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = get_document_chunks(doc_id)
    doc["chunks_count"] = len(chunks)
    return doc

@router.delete("/{doc_id}")
def remove_document(doc_id: str):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(doc_id)
    return {"status": "success", "message": f"Document '{doc['filename']}' deleted"}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_file"
    ext = Path(filename).suffix.lower()
    
    if ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="Only .pdf, .txt, and .md files are supported")

    doc_id = str(uuid.uuid4())
    save_path = UPLOADS_DIR / f"{doc_id}_{filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)

    try:
        if ext == ".pdf":
            full_text, pages, total_pages = extract_text_from_pdf(str(save_path))
        else:
            full_text, pages, total_pages = extract_text_from_txt(str(save_path))

        if not full_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any readable text from this file")

        metrics = get_text_metrics(full_text)
        chunks = chunk_text(pages, chunk_size=settings.max_chunk_size, chunk_overlap=settings.chunk_overlap)

        # Generate a brief initial snippet
        summary_snip = full_text[:200].replace('\n', ' ') + "..."

        doc_data = {
            "id": doc_id,
            "filename": filename,
            "file_type": ext.replace(".", ""),
            "file_size": file_size,
            "page_count": total_pages,
            "character_count": metrics["character_count"],
            "word_count": metrics["word_count"],
            "summary": summary_snip,
            "content": full_text
        }

        insert_document(doc_data, chunks)

        return {
            "status": "success",
            "document": {
                "id": doc_id,
                "filename": filename,
                "page_count": total_pages,
                "word_count": metrics["word_count"],
                "reading_time_minutes": metrics["reading_time_minutes"],
                "chunks_count": len(chunks)
            }
        }
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/upload-text")
def upload_raw_text(payload: TextUploadRequest):
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    doc_id = str(uuid.uuid4())
    filename = f"{payload.title.strip()}.txt"
    cleaned = clean_text(payload.content)
    metrics = get_text_metrics(cleaned)
    pages = [{"page_number": 1, "text": cleaned}]
    chunks = chunk_text(pages, chunk_size=settings.max_chunk_size, chunk_overlap=settings.chunk_overlap)

    summary_snip = cleaned[:200].replace('\n', ' ') + "..."

    doc_data = {
        "id": doc_id,
        "filename": filename,
        "file_type": "txt",
        "file_size": len(cleaned.encode('utf-8')),
        "page_count": 1,
        "character_count": metrics["character_count"],
        "word_count": metrics["word_count"],
        "summary": summary_snip,
        "content": cleaned
    }

    insert_document(doc_data, chunks)

    return {
        "status": "success",
        "document": {
            "id": doc_id,
            "filename": filename,
            "page_count": 1,
            "word_count": metrics["word_count"],
            "reading_time_minutes": metrics["reading_time_minutes"],
            "chunks_count": len(chunks)
        }
    }

@router.post("/load-samples")
def load_sample_documents():
    loaded = []
    for topic in SAMPLE_TOPICS:
        # Check if already loaded
        existing = get_document_by_id(topic["id"])
        if existing:
            continue

        full_text = "\n\n".join([f"--- [Page {p['page_number']}] ---\n" + p['text'] for p in topic["pages"]])
        metrics = get_text_metrics(full_text)
        chunks = chunk_text(topic["pages"], chunk_size=settings.max_chunk_size, chunk_overlap=settings.chunk_overlap)

        doc_data = {
            "id": topic["id"],
            "filename": topic["filename"],
            "file_type": "sample",
            "file_size": topic["file_size"],
            "page_count": topic["page_count"],
            "character_count": metrics["character_count"],
            "word_count": metrics["word_count"],
            "summary": topic["summary"],
            "content": full_text
        }
        insert_document(doc_data, chunks)
        loaded.append(topic["filename"])

    return {"status": "success", "loaded": loaded}

