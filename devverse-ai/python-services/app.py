from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from resume_analyzer.analyzer import analyze_resume
from knowledge_base.kb import add_document, search_knowledge
from code_executor.executor import execute_python_code
from interview_ai.analyzer import analyze_code_with_ai

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api/python-health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Python AI Service is running"})

@app.route('/api/resume/analyze', methods=['POST'])
def analyze_resume_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    job_description = request.form.get('job_description', '')
        
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    result = analyze_resume(filepath, job_description)
    
    # Cleanup
    try:
        os.remove(filepath)
    except:
        pass
        
    return jsonify(result)


from knowledge_base.kb import add_document, search_knowledge, remove_document, list_documents, get_document_text

# ---- KNOWLEDGE BASE ----

@app.route('/api/kb/upload', methods=['POST'])
def kb_upload():
    """Upload a file (PDF/TXT/MD) to index in the KB."""
    title = request.form.get('title', 'Untitled')
    tags  = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
    doc_id = request.form.get('doc_id', title.lower().replace(' ','-'))

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.pdf', '.txt', '.md']:
            return jsonify({"error": "Only PDF, TXT, MD files supported"}), 400
        filepath = os.path.join(UPLOAD_FOLDER, f"{doc_id}{ext}")
        file.save(filepath)
        ok, info = add_document(doc_id, "", title=title, tags=tags, filepath=filepath)
        try: os.remove(filepath)
        except: pass
    else:
        text = request.form.get('text') or (request.json or {}).get('text', '')
        if not text:
            return jsonify({"error": "No file or text provided"}), 400
        ok, info = add_document(doc_id, text, title=title, tags=tags)

    if ok:
        return jsonify({"message": "Indexed successfully", "info": info})
    return jsonify({"error": info}), 500


@app.route('/api/kb/index', methods=['POST'])
def kb_index_text():
    """Legacy: index raw text."""
    data   = request.json or {}
    doc_id = data.get('doc_id')
    text   = data.get('text')
    title  = data.get('title', doc_id or 'Untitled')
    tags   = data.get('tags', [])
    if not doc_id or not text:
        return jsonify({"error": "doc_id and text required"}), 400
    ok, info = add_document(doc_id, text, title=title, tags=tags)
    if ok:
        return jsonify({"message": "Document indexed", "info": info})
    return jsonify({"error": info}), 500


@app.route('/api/kb/search', methods=['POST'])
def kb_search():
    data   = request.json or {}
    query  = data.get('query', '')
    top_k  = int(data.get('top_k', 5))
    tags   = data.get('tags', None)
    if not query:
        return jsonify({"error": "query required"}), 400
    results = search_knowledge(query, top_k=top_k, tags=tags)
    return jsonify({"query": query, "results": results, "count": len(results)})


@app.route('/api/kb/documents', methods=['GET'])
def kb_list():
    return jsonify({"documents": list_documents()})


@app.route('/api/kb/document/<doc_id>', methods=['GET'])
def kb_get(doc_id):
    text = get_document_text(doc_id)
    if not text:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"doc_id": doc_id, "text": text})


@app.route('/api/kb/document/<doc_id>', methods=['DELETE'])
def kb_delete(doc_id):
    remove_document(doc_id)
    return jsonify({"message": f"Document '{doc_id}' removed from index"})



@app.route('/api/execute/python', methods=['POST'])
def execute_python():
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
        
    result = execute_python_code(code)
    return jsonify(result)

@app.route('/api/interview/analyze', methods=['POST'])
def analyze_interview():
    data = request.json
    question_title = data.get('question_title', '')
    code = data.get('code', '')
    language = data.get('language', 'javascript')

    if not code:
        return jsonify({"error": "No code provided"}), 400

    result = analyze_code_with_ai(question_title, code, language)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
