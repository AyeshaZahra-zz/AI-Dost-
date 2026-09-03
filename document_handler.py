import os
from pathlib import Path

def extract_text_from_file(file_path):
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.endswith('.pdf'):
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        elif file_path.endswith('.docx'):
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])
        else:
            return "Unsupported file type"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def explain_document(text, question):
    from llm_service import ask_qwen
    prompt = f"Document content:\n{text[:2000]}\n\nQuestion: {question}\n\nExplain this document in simple Urdu/English."
    return ask_qwen(prompt)