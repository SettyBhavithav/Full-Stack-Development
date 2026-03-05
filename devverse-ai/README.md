# DevVerse AI - Production Developer Platform

DevVerse AI is a comprehensive, modern SaaS platform combining multiple developer tools into a single ecosystem. It is built strictly using open-source tools and models (No Paid APIs).

## 🚀 Features

1. **Authentication:** Secure JWT-based Login/Signup.
2. **Real-time IDE:** Collaborative coding workspace using Monaco Editor and Socket.IO.
3. **Project Management:** Kanban board with SortableJS for drag-and-drop task tracking.
4. **AI Resume Parser:** NLP-driven resume parsing using Python `spaCy` to identify job skills.
5. **AI Knowledge Base:** RAG system powered by local FAISS vector store and Ollama (`llama3`).
6. **Background Tasks:** Redis + BullMQ (Node.js) asynchronous task queues.

## 🛠️ Tech Stack

- **Frontend:** Vanilla JS, HTML5, CSS3, Tailwind CSS, Monaco Editor, SortableJS, Chart.js
- **Backend (Node.js):** Express.js, Socket.IO, BullMQ, bcryptjs, jsonwebtoken, mysql2
- **AI Services (Python):** Flask, spaCy, PyPDF2, FAISS, Ollama
- **Database / Cache:** MySQL 8, Redis (via Docker)

---

## 💻 Local Setup Instructions

### Prerequisites
1. **Node.js**: v18+
2. **Python**: v3.10+
3. **Docker Desktop**: Must be installed and running.
4. **Ollama**: Must be running locally with `nomic-embed-text` and `llama3` models pulled (`ollama pull llama3`, `ollama pull nomic-embed-text`).

### 1. Start the Databases (Docker)
Ensure Docker Desktop is open and running in the background.
```powershell
cd docker
docker compose up -d
```
*Note: This starts `devverse_mysql` (with auto-injected schema) and `devverse_redis`.*

### 2. Start the Backend (Node.js & Socket.IO)
```powershell
cd backend
npm install
node server.js
```
*The API will run on http://localhost:5000*

### 3. Start Background Workers (Node.js)
In a separate terminal:
```powershell
cd workers
npm install bullmq axios
node queue_worker.js
```

### 4. Start Python AI Services (Flask)
```powershell
cd python-services
# Ensure Python dependencies are installed (Already done via setup script)
.\venv\Scripts\activate
# If running for the first time: pip install -r requirements.txt (spacy, flask, etc.)
python app.py
```
*The Python API will run on http://localhost:5001*

### 5. Open the Frontend
Since the frontend uses pure HTML/JS, you can simply open `frontend/index.html` in your web browser, or use a tool like Live Server.

---

> **Note:** Initial Docker startup for MySQL may take a minute to initialize the SQL schema from `database/schema.sql`.
