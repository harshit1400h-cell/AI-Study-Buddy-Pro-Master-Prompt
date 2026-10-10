import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import pypdf

def extract_text_from_pdf(file_path: str) -> Tuple[str, List[Dict[str, Any]], int]:
    """
    Extracts text from a PDF file page by page.
    Returns:
        - full_text: combined string of all extracted text
        - pages: list of dicts with page_number and page_text
        - total_pages: total number of pages
    """
    reader = pypdf.PdfReader(file_path)
    total_pages = len(reader.pages)
    pages = []
    full_text_parts = []

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        cleaned = clean_text(raw_text)
        if cleaned:
            pages.append({
                "page_number": page_num,
                "text": cleaned
            })
            full_text_parts.append(f"--- [Page {page_num}] ---\n" + cleaned)
        else:
            pages.append({
                "page_number": page_num,
                "text": "[No text extracted from this page - possibly scanned or empty]"
            })

    full_text = "\n\n".join(full_text_parts)
    return full_text, pages, total_pages

def extract_text_from_txt(file_path: str) -> Tuple[str, List[Dict[str, Any]], int]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()
    cleaned = clean_text(raw_text)
    pages = [{"page_number": 1, "text": cleaned}]
    return cleaned, pages, 1

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode spaces
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    # Fix broken hyphens at end of lines
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Collapse 3 or more newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple inline spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def chunk_text(pages: List[Dict[str, Any]], chunk_size: int = 800, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
    """
    Chunks text while preserving page number references for RAG citations.
    """
    chunks = []
    chunk_index = 0

    for page_info in pages:
        page_num = page_info["page_number"]
        page_text = page_info["text"]
        if not page_text or page_text.startswith("[No text"):
            continue

        # Split text into paragraphs first
        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
        
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + p
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_index,
                        "page_number": page_num,
                        "text": current_chunk.strip()
                    })
                    chunk_index += 1
                    # Overlap handling
                    overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                    current_chunk = (overlap_text + "\n" + p).strip()
                else:
                    # Paragraph itself exceeds chunk_size, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    for s in sentences:
                        if len(current_chunk) + len(s) <= chunk_size:
                            current_chunk += (" " if current_chunk else "") + s
                        else:
                            if current_chunk:
                                chunks.append({
                                    "chunk_index": chunk_index,
                                    "page_number": page_num,
                                    "text": current_chunk.strip()
                                })
                                chunk_index += 1
                            current_chunk = s

        if current_chunk:
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_num,
                "text": current_chunk.strip()
            })
            chunk_index += 1

    return chunks

def get_text_metrics(text: str) -> Dict[str, Any]:
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    char_count = len(text)
    # Average reading speed: 200 words per minute
    reading_time_minutes = max(1, round(word_count / 200))
    return {
        "word_count": word_count,
        "character_count": char_count,
        "reading_time_minutes": reading_time_minutes
    }

