"""
Knowledge Base Engine
- Supports PDF, TXT, MD document ingestion
- BM25 (Okapi BM25) full-text search — no external LLM needed
- In-memory document store (persisted via Flask API calls to MySQL from Node backend)
- Smart text chunking with overlap for better context retrieval
"""

import re
import math
import os
from collections import Counter



# ============================================================
# CONFIG
# ============================================================
CHUNK_SIZE    = 400   # words per chunk
CHUNK_OVERLAP = 80    # overlap to preserve context
BM25_K1 = 1.5
BM25_B  = 0.75

# In-memory store
_documents = []  # [{doc_id, title, tags, chunks: [{text, words}]}]
_full_texts = {}  # {doc_id: original_full_text} — preserved for reading


# ============================================================
# TEXT EXTRACTION
# ============================================================
def _fix_pdf_text(text):
    """Post-process PDF-extracted text to fix common artifacts."""
    import re
    # Fix words stuck together by inserting space before uppercase after lowercase
    # e.g. "allclients" won't be fixed (can't know), but "Consistency:Consistency" → "Consistency: Consistency"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase split
    text = re.sub(r'([.:,;!?])([A-Za-z])', r'\1 \2', text)  # fix "word.word"
    # Fix multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Normalise line endings
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            # Try pdfplumber first (better layout-aware extraction)
            try:
                import pdfplumber
                pages_text = []
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text(layout=True) or ""
                        if page_text.strip():
                            pages_text.append(page_text)
                text = "\n\n".join(pages_text)
                return _fix_pdf_text(text)
            except ImportError:
                pass  # fall through to PyPDF2

            # Fallback: PyPDF2 (older, lower quality)
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            pages = []
            for page in reader.pages:
                t = page.extract_text() or ""
                if t.strip():
                    pages.append(t)
            text = "\n".join(pages)
            return _fix_pdf_text(text)

        else:  # .txt, .md, or any text file
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return ""


def extract_text_from_string(text):
    return text


# ============================================================
# TEXT PROCESSING
# ============================================================
STOP_WORDS = {
    "the", "is", "in", "it", "of", "to", "a", "and", "or", "for", "on",
    "with", "this", "that", "be", "as", "at", "by", "an", "are", "was",
    "we", "i", "you", "he", "she", "they", "do", "not", "but", "from",
    "have", "has", "had", "will", "can", "so", "if", "which", "who",
    "all", "been", "its", "also", "more", "their", "there", "than"
}

def tokenize(text):
    """Lowercase, strip punctuation, remove stopwords."""
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_\-]*\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    step = max(chunk_size - overlap, 1)
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        if len(chunk_words) >= 20:  # Skip tiny trailing chunks
            chunks.append({"text": chunk_text, "words": tokenize(chunk_text), "offset": i})
    return chunks or [{"text": text[:2000], "words": tokenize(text[:2000]), "offset": 0}]


def generate_excerpt(text, query_tokens, max_words=50):
    """Find a relevant excerpt from a chunk around query keywords."""
    words = text.split()
    best_start = 0
    best_hits  = 0
    for i in range(len(words)):
        window = words[i:i+max_words]
        hits = sum(1 for w in window if w.lower() in query_tokens)
        if hits > best_hits:
            best_hits  = hits
            best_start = i
    snippet = " ".join(words[best_start:best_start+max_words])
    return snippet + ("…" if best_start + max_words < len(words) else "")


# ============================================================
# BM25 ENGINE
# ============================================================
class BM25Index:
    def __init__(self):
        self.docs   = []  # list of {"doc_id", "title", "tags", "chunk_idx", "text", "words"}
        self.idf    = {}
        self.avgdl  = 0
        self._dirty = True

    def add_doc(self, doc_id, title, tags, chunks):
        for i, chunk in enumerate(chunks):
            self.docs.append({
                "doc_id":    doc_id,
                "title":     title,
                "tags":      tags,
                "chunk_idx": i,
                "text":      chunk["text"],
                "words":     chunk["words"],
            })
        self._dirty = True

    def remove_doc(self, doc_id):
        self.docs = [d for d in self.docs if d["doc_id"] != doc_id]
        self._dirty = True

    def _build_idf(self):
        N = len(self.docs)
        if N == 0:
            self.idf = {}
            self.avgdl = 0
            self._dirty = False
            return
        df = Counter()
        total_len = 0
        for doc in self.docs:
            total_len += len(doc["words"])
            for word in set(doc["words"]):
                df[word] += 1
        self.avgdl = total_len / N
        self.idf = {
            w: math.log((N - n + 0.5) / (n + 0.5) + 1)
            for w, n in df.items()
        }
        self._dirty = False

    def search(self, query, top_k=5, tag_filter=None):
        if self._dirty:
            self._build_idf()
        if not self.docs:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = []
        for doc in self.docs:
            if tag_filter and not any(t.lower() in [x.lower() for x in doc["tags"]] for t in tag_filter):
                continue
            tf = Counter(doc["words"])
            dl = len(doc["words"])
            score = 0.0
            for q in query_tokens:
                if q not in self.idf:
                    continue
                f = tf.get(q, 0)
                num = f * (BM25_K1 + 1)
                den = f + BM25_K1 * (1 - BM25_B + BM25_B * dl / max(self.avgdl, 1))
                score += self.idf[q] * (num / max(den, 1e-9))
            if score > 0:
                scores.append((score, doc))

        scores.sort(key=lambda x: -x[0])

        # Deduplicate by doc_id — return best chunk per doc
        seen_docs = {}
        results = []
        for score, doc in scores:
            if doc["doc_id"] not in seen_docs:
                seen_docs[doc["doc_id"]] = score
                results.append({
                    "doc_id":  doc["doc_id"],
                    "title":   doc["title"],
                    "tags":    doc["tags"],
                    "score":   round(score, 3),
                    "excerpt": generate_excerpt(doc["text"], set(query_tokens)),
                    "full_text": doc["text"],
                })
            if len(results) >= top_k:
                break
        return results


# Global index
_index = BM25Index()


# ============================================================
# PUBLIC API
# ============================================================
def add_document(doc_id, text, title="Untitled", tags=None, filepath=None):
    """
    Add a document to the knowledge base.
    - If filepath is given, extract text from it.
    - text can also be raw content.
    """
    try:
        if filepath and os.path.exists(filepath):
            content = extract_text_from_file(filepath)
        else:
            content = text or ""

        if not content.strip():
            return False, "No content to index"

        chunks = chunk_text(content)
        _index.remove_doc(doc_id)  # remove old version if exists
        _index.add_doc(doc_id, title or "Untitled", tags or [], chunks)
        _full_texts[doc_id] = content  # store original for full-text reading

        return True, {
            "doc_id": doc_id,
            "title": title,
            "tags": tags or [],
            "chunks": len(chunks),
            "word_count": len(content.split()),
            "excerpt": " ".join(content.split()[:40]) + "…",
        }
    except Exception as e:
        return False, str(e)


def remove_document(doc_id):
    _index.remove_doc(doc_id)
    _full_texts.pop(doc_id, None)
    return True


def search_knowledge(query, top_k=5, tags=None):
    """
    BM25 search across all indexed documents.
    Returns list of results with doc_id, title, score, excerpt.
    """
    if not query or not query.strip():
        return []
    return _index.search(query, top_k=top_k, tag_filter=tags)


def list_documents():
    """Return unique doc metadata from index."""
    seen = {}
    for doc in _index.docs:
        if doc["doc_id"] not in seen:
            seen[doc["doc_id"]] = {
                "doc_id": doc["doc_id"],
                "title":  doc["title"],
                "tags":   doc["tags"],
                "chunks": 0,
            }
        seen[doc["doc_id"]]["chunks"] += 1
    return list(seen.values())


def get_document_text(doc_id):
    """Return the original full text of a document (structure preserved)."""
    # Prefer original stored text (has line breaks, structure)
    if doc_id in _full_texts:
        return _full_texts[doc_id]
    # Fallback: join chunks (loses structure but at least returns something)
    chunks = [d["text"] for d in _index.docs if d["doc_id"] == doc_id]
    return "\n\n".join(chunks)
