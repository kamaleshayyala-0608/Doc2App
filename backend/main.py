from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import json
import shutil
import zipfile

from utils.file_handler import save_extracted_text
from parsers.pdf_parser import extract_pdf_text
from parsers.docx_parser import extract_docx_text
from parsers.txt_parser import extract_txt_text
from parsers.markdown_parser import extract_md_text

from rag.chunker import create_chunks
from rag.embedder import create_embeddings, get_model
from rag.vector_store import create_faiss_index
from rag.retriever import retrieve_chunks

from generators.requirement_generator import generate_requirements
from generators.architecture_generator import generate_architecture
from generators.project_builder import ProjectBuilder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database to store RAG index across endpoints
db = {
    "text": "",
    "chunks": [],
    "index": None
}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    extension = file.filename.split(".")[-1].lower()
    text = ""
    
    if extension == "pdf":
        text = extract_pdf_text(file_path)
    elif extension == "docx":
        text = extract_docx_text(file_path)
    elif extension == "txt":
        text = extract_txt_text(file_path)
    elif extension == "md":
        text = extract_md_text(file_path)
        
    save_extracted_text(file.filename, text)
    
    chunks = create_chunks(text)
    embeddings = create_embeddings(chunks)
    index = create_faiss_index(embeddings)
    
    db["text"] = text
    db["chunks"] = chunks
    db["index"] = index
    
    return {"message": "Document uploaded successfully", "characters": len(text)}

@app.post("/generate-requirements")
async def api_generate_requirements():
    model = get_model()
    query = "Summarize the software requirements."
    
    relevant_chunks = retrieve_chunks(
        query, model, db["index"], db["chunks"], top_k=10
    )
    
    context = "\n".join(relevant_chunks)
    requirements = generate_requirements(context)
    
    os.makedirs("generated_projects", exist_ok=True)
    with open("generated_projects/requirements.json", "w", encoding="utf-8") as f:
        f.write(requirements)
        
    return {"requirements": requirements}

@app.post("/generate-architecture")
async def api_generate_architecture():
    with open("generated_projects/requirements.json", "r", encoding="utf-8") as f:
        requirements = f.read()
        
    architecture = generate_architecture(requirements)
    
    with open("generated_projects/architecture.json", "w", encoding="utf-8") as f:
        f.write(architecture)
        
    return {"architecture": architecture}

@app.post("/build-project")
async def build_project():
    try:
        print("Building project...")
        
        with open("generated_projects/architecture.json", "r", encoding="utf-8") as f:
            architecture = f.read()
            
        builder = ProjectBuilder()
        builder.build(architecture)
        
        print("Project generation finished")
        return {"status": "success", "message": "Project generated successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/download-project")
async def download_project():
    project_folder = "generated_projects/project"
    zip_name = "generated_projects/generated_project.zip"

    # Validate that files actually exist before zipping
    file_count = 0
    if os.path.exists(project_folder):
        for _, _, files in os.walk(project_folder):
            file_count += len(files)

    if file_count == 0:
        return {
            "status": "error",
            "message": "Project contains no generated files."
        }

    os.makedirs(os.path.dirname(zip_name), exist_ok=True)

    with zipfile.ZipFile(
        zip_name,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for root, dirs, files in os.walk(project_folder):
            # Exclude large or unnecessary directories
            dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__', 'venv', '.venv', '.git')]

            for file in files:
                path = os.path.join(root, file)
                
                # Ensure forward slashes for zip archive paths
                arcname = os.path.relpath(path, project_folder).replace("\\", "/")

                zipf.write(
                    path,
                    arcname
                )

    return FileResponse(
        zip_name,
        media_type="application/zip",
        filename="generated_project.zip"
    )
