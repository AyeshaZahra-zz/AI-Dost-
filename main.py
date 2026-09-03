from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_service import ask_qwen
from document_handler import extract_text_from_file, explain_document
from typing import List
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class Question(BaseModel):
    text: str
    language: str = "urdu"
    history: List[Message] = []

@app.post("/ask")
async def ask_question(q: Question):
    context = ""
    if q.history:
        context = "Previous: " + str([m.content[:50] for m in q.history[-2:]]) + "\n"
    
    full_question = context + q.text
    answer = ask_qwen(full_question, q.language)
    return {"response": answer, "language": q.language}

@app.post("/explain-document")
async def explain_doc(file: UploadFile = File(...), question: str = "Explain this"):
    file_path = f"temp_{file.filename}"
    
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    text = extract_text_from_file(file_path)
    answer = explain_document(text, question)
    
    os.remove(file_path)
    return {"response": answer}

@app.get("/health")
async def health():
    return {"status": "ok", "ai": "Alibaba Qwen", "services": 12}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)