# DevVerse AI - Production Developer Platform

DevVerse AI is a comprehensive, modern SaaS platform combining multiple developer tools into a single ecosystem. It is built to empower developers with built-in AI tools, integrated workspaces, and intelligent assistance—using open-source models and intelligent local processing.

![DevVerse AI Overview](./frontend/assets/logo.png) <!-- Update this path if you have a real banner/logo -->

## 🚀 Key Features

### 1. 📊 Developer Dashboard
A unified command center providing a bird's-eye view of your productivity.
- **Activity Metrics:** Tracks commits, active projects, and upcoming AI mock interviews.
- **Quick Actions:** Jump straight into coding, task planning, or resume optimization with one click.
- **Dynamic Styling:** Built with a premium, responsive glassmorphism dark-theme UI using TailwindCSS.

### 2. 💻 AI-Powered IDE Workspace
A collaborative, browser-based coding environment.
- **Monaco Editor Integration:** Industry-standard code editing experience (same engine as VS Code).
- **Real-Time Collaboration:** Powered by Node.js and Socket.IO for live pair programming.
- **Multi-Language Support:** Write, run, and execute Python and JavaScript code directly in the browser.
- **AI Code Assistant:** Integrated AI helper to debug, explain, and optimize your code on the fly.

### 3. 📋 Intelligent Project Planner
A visual Kanban board for agile development tracking.
- **Drag-and-Drop Columns:** Powered by SortableJS for smooth task management (To Do, In Progress, Review, Done).
- **Rich Task Details:** Tagging, priority indicators, and assignee tracking.
- **Automated Workflows:** Seamlessly integrated with the backend database for persistent state management.

### 4. 🧠 AI Knowledge Base (RAG System)
A locally-indexed document management system for instant context retrieval.
- **Multi-Format Ingestion:** Upload PDEs, Markdown, and TXT files.
- **Layout-Aware Extraction:** Uses `pdfplumber` for superior text parsing that preserves line breaks, lists, and headings.
- **BM25 Instant Search:** Lightning-fast, full-text semantic search using an Okapi BM25 engine.
- **Inline Reader Panel:** Read documents side-by-side with your search results without opening new tabs.

### 5. 📄 Smart Resume Analyzer
Optimize your resume against specific job descriptions.
- **NLP Parsing:** Utilizes Python's `spaCy` to extract skills, experience, and keywords.
- **Match Scoring:** Calculates a precise compatibility score between your resume and the target job description.
- **Actionable Feedback:** Identifies missing keywords and provides concrete suggestions to improve your ATS ranking.

### 6. 🎙️ AI Mock Interviews
Practice technical interviews with an intelligent AI evaluator.
- **Real-Time Code Evaluation:** Write code to solve algorithmic challenges while the AI analyzes your approach.
- **Constructive Feedback:** Receives graded assessments on logic, efficiency, and code quality.

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JS, Tailwind CSS, Monaco Editor, SortableJS, Lucide Icons, Chart.js
- **Backend (Node.js):** Express.js, Socket.IO, BullMQ, bcryptjs, jsonwebtoken, mysql2
- **AI Services (Python):** Flask, pdfplumber, spaCy, PyPDF2
- **Database / Infrastructure:** MySQL 8, Redis (via Docker)

---

## 💻 Local Setup Instructions

### Prerequisites
1. **Node.js**: v18+
2. **Python**: v3.10+
3. **Docker Desktop**: Must be installed and running.

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
# If running for the first time: pip install -r requirements.txt (spacy, flask, pdfplumber, etc.)
python app.py
```
*The Python API will run on http://localhost:5001*

### 5. Run the Application
You can launch the entire ecosystem with a single click using the provided launchers in the root directory:
- **`DevVerse.bat`** (Windows Batch script)
- **`Launch.vbs`** (Silent background launcher)
- **`index.hta`** (Desktop application wrapper)

Alternatively, just serve `frontend/index.html` via Live Server.

---

> **Note:** Initial Docker startup for MySQL may take a minute to initialize the SQL schema from `database/schema.sql`.
