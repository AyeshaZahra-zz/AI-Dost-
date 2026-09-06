from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_service import ask_qwen
from document_handler import extract_text_from_file, explain_document
from typing import List
from dotenv import load_dotenv
import os
import base64


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Dost",
    description="AI Dost - Pakistan Government Services Assistant",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA MODELS
# ============================================================

class Message(BaseModel):
    role: str
    content: str


class Question(BaseModel):
    text: str
    language: str = "auto"
    history: List[Message] = []


# ============================================================
# ASK AI
# ============================================================

@app.post("/ask")
async def ask_question(q: Question):

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    context = ""

    if q.history:

        previous_messages = [
            m.content[:200]
            for m in q.history[-4:]
        ]

        context = (
            "Previous conversation:\n"
            + "\n".join(previous_messages)
            + "\n\n"
        )


    # --------------------------------------------------------
    # Language instructions
    # --------------------------------------------------------

    instructions = """
You are AI Dost, a friendly and helpful AI assistant for
Pakistan government and public services.

IMPORTANT LANGUAGE RULES:

1. Detect the language of the user's CURRENT question.

2. If the user writes in English:
   ALWAYS answer in English.

3. If the user writes in Roman Urdu:
   ALWAYS answer in Roman Urdu.

4. If the user writes in Urdu script:
   ALWAYS answer in Urdu script.

5. If the user mixes English and Urdu:
   Naturally use the same mixed style.

6. If the user uses another language:
   Try to answer in that same language.

7. NEVER answer an English question in Urdu.

8. NEVER answer a Roman Urdu question in Urdu script unless
   the user specifically asks for Urdu script.

9. Match the user's tone and communication style.

10. Use EASY and EVERYDAY words.

11. Keep simple questions short.

12. If the user asks for a process, give numbered steps.

13. Do not unnecessarily translate the user's question.

14. Never invent government information.

15. If information may have changed, tell the user to verify
    it from the relevant official government department.

Pakistan government services include:

- NADRA
- CNIC
- Healthcare
- Education
- Scholarships
- FBR
- Taxes
- Pensions
- BISP
- Other public services
"""


    # --------------------------------------------------------
    # Create final question
    # --------------------------------------------------------

    full_question = f"""
{instructions}

{context}

IMPORTANT:
The CURRENT USER QUESTION determines the answer language.

Current user question:
{q.text}

Remember:
English question = English answer.
Roman Urdu question = Roman Urdu answer.
Urdu script question = Urdu script answer.
Mixed question = same mixed style.
"""


    # --------------------------------------------------------
    # Ask Qwen
    # --------------------------------------------------------

    try:

        answer = ask_qwen(
            full_question,
            q.language
        )

    except Exception as e:

        print("AI Error:", str(e))

        answer = (
            "Sorry, I am having trouble answering right now. "
            "Please try again."
        )


    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "response": answer,
        "language": q.language
    }


# ============================================================
# DOCUMENT EXPLANATION
# ============================================================

@app.post("/explain-document")
async def explain_doc(
    file: UploadFile = File(...),
    question: str = "Explain this"
):

    file_path = f"temp_{file.filename}"

    try:

        # Save uploaded file
        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)


        # Extract text
        text = extract_text_from_file(file_path)


        # Explain document
        answer = explain_document(
            text,
            question
        )


        return {
            "response": answer
        }


    finally:

        # Delete temporary file
        if os.path.exists(file_path):

            os.remove(file_path)


# ============================================================
# TEXT TO SPEECH
# ============================================================

@app.post("/tts")
async def text_to_speech(data: dict):

    try:

        from dashscope import SpeechSynthesis

        text = data.get("text", "").strip()

        if not text:

            return {
                "status": "error",
                "message": "No text provided"
            }


        # Get API key from .env
        API_KEY = os.getenv("DASHSCOPE_API_KEY")

        if not API_KEY:

            return {
                "status": "error",
                "message": "DASHSCOPE_API_KEY is not configured"
            }


        # Clean text
        text = (
            text
            .replace("<", "")
            .replace(">", "")
            .replace("&", "")
        )


        # Generate speech
        synthesis = SpeechSynthesis.call(
            model="cosyvoice-v1",
            text=text,
            voice="default",
            api_key=API_KEY
        )


        audio_data = synthesis.get_audio_data()


        if audio_data:

            encoded_audio = base64.b64encode(
                audio_data
            ).decode("utf-8")

            return {
                "audio": encoded_audio,
                "status": "success"
            }


        return {
            "status": "error",
            "message": "No audio was generated"
        }


    except Exception as e:

        print("TTS Error:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "ai": "Alibaba Qwen",
        "services": 12
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )