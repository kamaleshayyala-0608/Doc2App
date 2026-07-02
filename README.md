# 📄 Doc2App Lite 

Doc2App Lite is a local, AI-powered development tool that takes plain text software documentation (PDF, DOCX, TXT, Markdown) and automatically generates a fully structured starter codebase. 

Instead of going from documentation straight to code, this tool mimics a real software engineer's workflow by breaking the process down into logical phases:

**Document ➡️ Requirements ➡️ Architecture Blueprint ➡️ Code Generation**

---

## ✨ Features

- **Multi-format Document Parsing**: Extract text from PDFs, DOCX, TXT, and Markdown files.
- **Retrieval-Augmented Generation (RAG)**: Uses `sentence-transformers` and `FAISS` to chunk and search large documents.
- **100% Local AI**: Powered by [Ollama](https://ollama.com/) running locally with the `qwen2.5-coder:3b` model for complete privacy.
- **Structured Requirements**: Automatically extracts features, roles, and tech stacks into a clean JSON format.
- **Blueprint Generation**: Plans the architecture (folders, pages, APIs, schemas) before writing any code.
- **Advanced File-by-File Generation**: Employs an intelligent multi-agent pipeline that plans a manifest, writes code file-by-file, validates syntax/imports, and attempts to resolve dependencies.
- **Modern Tech Stack**: React frontend with a sleek glassmorphism UI, decoupled from a fast and highly responsive FastAPI Python backend.

---

## 🛠️ Project Structure

```text
doc2app-lite/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # FastAPI entrypoint (Endpoints: /upload, /generate-*, /build-project)
│   ├── parsers/                      # PyMuPDF, python-docx extractors
│   ├── rag/                          # Embeddings, chunking, and FAISS indexing
│   ├── llm/                          # Ollama client and AI prompts
│   ├── generators/                   # Advanced AI agent pipeline (manifest, builder, validator)
│   ├── memory/                       # Short-term AI memory for context-aware generation
│   └── utils/                        # File handling and JSON parsing
│
├── frontend/                         # React Vite App
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx                   # React Router
│       ├── index.css                 # Global styling and aesthetics
│       ├── services/
│       │   └── api.js                # Axios configuration connecting to FastAPI
│       └── pages/                    # UI flow (Upload -> Requirements -> Architecture -> Project)
│
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Node.js** (for the React frontend)
- **Python 3.10+** (for the FastAPI backend)
- **Ollama**: Download from [ollama.com](https://ollama.com/)

### 2. Download the Local LLM
Ensure Ollama is installed, then open a terminal and pull the Qwen coder model:
```bash
ollama pull qwen2.5-coder:3b
```

### 3. Backend Setup
Open a terminal in the `doc2app-lite` directory and install the required packages:
```bash
pip install -r requirements.txt
```
*Note: Make sure FastAPI, Uvicorn, and python-multipart are installed!*

### 4. Frontend Setup
Open another terminal, navigate into the `frontend/` folder, and install NPM packages:
```bash
cd frontend
npm install
```

---

## 🎮 Usage

You will need **three** terminal windows running simultaneously to power the application:

1. **Start the Ollama Server** 
   ```bash
   ollama serve
   ```

2. **Start the FastAPI Backend**
   Navigate to the `backend/` directory inside `doc2app-lite`:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. **Start the React Frontend**
   Navigate to the `frontend/` directory inside `doc2app-lite`:
   ```bash
   cd frontend
   npm run dev
   ```

Open your browser to `http://localhost:5173` (or the port Vite provides).

### Generate your App (The Workflow)
- **Step 1 (Upload)**: Drag & Drop your software documentation.
- **Step 2 (Requirements)**: The AI will parse the document and extract the core JSON requirements.
- **Step 3 (Architecture)**: Generates the planned backend, frontend, and database blueprint.
- **Step 4 (Build)**: The AI orchestrates a multi-agent file-by-file generation pipeline. Watch your terminal as it builds the manifest, iteratively writes and validates each file, and installs dependencies. Click **Download Source Code (ZIP)** to save your new starter project!
