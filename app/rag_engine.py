uimport re
import math
from typing import List, Dict, Any, Optional
from app.database import get_document_chunks, get_document_by_id

class SimpleRAGSearcher:
    """
    Fast and accurate in-memory retrieval engine using BM25/TF-IDF token scoring.
    No external heavy vector database required, ultra-fast and reliable on any machine.
    """
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        # Lowercase, alphanumeric words, filter very short stopwords
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'what', 'which', 'who', 'this'
        }
        tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        return [t for t in tokens if t not in stopwords]

    @classmethod
    def search(cls, query: str, document_id: Optional[str] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        chunks = get_document_chunks(document_id)
        if not chunks:
            return []

        query_tokens = cls.tokenize(query)
        if not query_tokens:
            # Return first few chunks if empty query
            return chunks[:top_k]

        # Calculate Document Frequency (DF) across chunks
        df = {}
        chunk_token_lists = []
        for c in chunks:
            tokens = set(cls.tokenize(c['text']))
            chunk_token_lists.append(tokens)
            for t in tokens:
                df[t] = df.get(t, 0) + 1

        total_chunks = len(chunks)
        scores = []

        for idx, chunk in enumerate(chunks):
            tokens = chunk_token_lists[idx]
            chunk_text = chunk['text'].lower()
            score = 0.0

            # Match exact phrase bonus
            if query.lower() in chunk_text:
                score += 5.0

            for q_term in query_tokens:
                if q_term in tokens:
                    # IDF calculation
                    term_df = df.get(q_term, 1)
                    idf = math.log((total_chunks + 1) / (term_df + 0.5)) + 1.0
                    # Term count in chunk
                    tf = chunk_text.count(q_term)
                    score += (tf * idf)

            if score > 0:
                # Add snippet
                snippet = chunk['text'][:250] + ("..." if len(chunk['text']) > 250 else "")
                scores.append({
                    "score": round(score, 2),
                    "chunk_id": chunk['id'],
                    "document_id": chunk['document_id'],
                    "page_number": chunk.get('page_number', 1),
                    "text": chunk['text'],
                    "snippet": snippet
                })

        # Sort descending by score
        scores.sort(key=lambda x: x['score'], reverse=True)
        results = scores[:top_k]

        # If zero matches found through keywords, return top chunks with a default score
        if not results:
            for c in chunks[:top_k]:
                snippet = c['text'][:250] + ("..." if len(c['text']) > 250 else "")
                results.append({
                    "score": 0.5,
                    "chunk_id": c['id'],
                    "document_id": c['document_id'],
                    "page_number": c.get('page_number', 1),
                    "text": c['text'],
                    "snippet": snippet
                })

        return results

