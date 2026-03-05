## 📚 AI Knowledge Base

The Knowledge Base is a powerful, locally-indexed document management system built directly into DevVerse AI. It allows you to upload project documentation, textbooks, or personal notes and instantly search across all of them without relying on external APIs or vector databases.

### Key Features
* **Multi-Format Support**: Instantly ingest **PDFs**, **Markdown (.md)**, and **Plain Text (.txt)** files, or paste raw text directly into the UI.
* **Layout-Aware PDF Extraction**: Utilizes `pdfplumber` for high-quality text extraction that preserves original line breaks, bullet points, and document structure.
* **Smart Content Formatting**: A custom, intelligent text pre-processor recognizes and re-formats:
  * Numbered lists (`1.`, `2.`) and bullet points (`•`, `-`)
  * Section headings, subheadings, and title-cased labels
  * Question-style headings and bold/code text wrappers
* **Instant BM25 Search**: Lightning-fast, full-text search using the Okapi BM25 algorithm. Finds the most relevant chunks of text across your entire library in milliseconds.
* **Inline Document Reader**: A sleek, non-blocking slide-in reader panel that lets you read documents side-by-side with your library. 
  * Features include: Reading time estimates, dynamic typography sizing (`A-`/`A+`), and "Find in document" highlighting.
* **Tagging & Organization**: Tag your documents upon upload for easy filtering and categorization within the grid or list views.

### How It Works (Under the Hood)
1. **Ingestion**: Documents are parsed in Python. PDFs undergo an artifact-cleaning process to fix common extraction issues (e.g., stuck words, missing spaces).
2. **Chunking**: Text is split into overlapping 400-word chunks to preserve context.
3. **Indexing**: Processed chunks are tokenized (stop-words removed) and stored in an in-memory TF-IDF/BM25 index for zero-latency retrieval.
4. **Retrieval**: Search queries are scored against the index, and the system intelligently returns the highest-scoring contextual excerpt along with the full, original document structure.
