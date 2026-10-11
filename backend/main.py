
from pathlib import Path
import asyncio
import subprocess
import uuid
from typing import Optional

import chromadb
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.database import (
    SessionLocal,
    ChatSession,
    ChatMessage,
)


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

app = FastAPI(title="Lenny Growth Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"

CHAT_MODEL = "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"

NODE_COMMAND = r"C:\Program Files\nodejs\node.exe"
PI_SCRIPT = str(Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "@mariozechner" / "pi-coding-agent" / "dist" / "cli.js")
PI_TIMEOUT = 600

PROJECT_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = PROJECT_DIR / "data" / "vector_db"


# --------------------------------------------------
# Load the existing ChromaDB index
# --------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_PATH)
)

collection = chroma_client.get_collection(
    name="lenny_sources"
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
class WritingRequest(BaseModel):
    topic: str


# --------------------------------------------------
# Basic endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Lenny Growth Assistant"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "indexed_chunks": collection.count()
    }


# --------------------------------------------------
# Pi Coding Agent integration
# --------------------------------------------------

async def ask_pi(prompt: str) -> str:
    """Run Pi with the local Ollama model."""

    def run_pi():
        return subprocess.run(
            [
                NODE_COMMAND,
                PI_SCRIPT,
                "--provider", "ollama",
                "--model", CHAT_MODEL,
                "--no-session",
                "--no-tools",
                "--system-prompt",
                (
    "You are Lenny Growth Assistant, an assistant that answers "
    "questions using Lenny's podcast and newsletter transcripts. "
    "The user prompt contains retrieved transcript passages, "
    "conversation history, and the current question. "
    "The passages are already provided; never ask the user to "
    "provide them again. Read the passages carefully and answer "
    "using relevant information from them. "
    "If the passages do not contain enough information, explain "
    "what is missing. Do not invent facts or citations. "
    "Mention the filenames of the sources that support your answer."
),
                "-p", prompt,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PI_TIMEOUT,
            cwd=str(PROJECT_DIR),
            shell=False,
        )

    try:
        result = await asyncio.to_thread(run_pi)

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail="The AI response timed out. Please try again."
        ) from exc

    except OSError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not start Pi Coding Agent."
        ) from exc

    if result.returncode != 0:
        raise HTTPException(
            status_code=502,
            detail=(
                "Pi could not generate a response: "
                f"{result.stderr[-500:]}"
            )
        )

    reply = result.stdout.strip()

    if not reply:
        raise HTTPException(
            status_code=502,
            detail="Pi returned an empty response."
        )

    return reply


# --------------------------------------------------
# Generate embeddings using Ollama
# --------------------------------------------------

async def get_embedding(text: str):
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_EMBED_URL,
            json={
                "model": EMBED_MODEL,
                "input": "search_query: " + text
            }
        )

        response.raise_for_status()
        data = response.json()

    return data["embeddings"][0]


# --------------------------------------------------
# Retrieve relevant transcript passages
# --------------------------------------------------

async def retrieve_sources(question: str):
    query_embedding = await get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=6,
        include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n--- RETRIEVAL DEBUG ---")
    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        print("Source:", metadata.get("source", "Unknown"))
        print("Chunk:", metadata.get("chunk", -1))
        print("Distance:", round(distance, 4))
        print("Text:", document[:250].replace("\n", " "))
        print("-" * 40)

    sources = []
    for document, metadata in zip(documents, metadatas):
        sources.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "chunk": metadata.get("chunk", -1)
        })

    return sources

# --------------------------------------------------
# Load previous conversation messages
# --------------------------------------------------

def load_history(db, session_id: str):
    records = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(10)
    ).all()

    # Reverse newest-first results to chronological order.
    records.reverse()

    return [
        {
            "role": record.role,
            "content": record.content
        }
        for record in records
        if record.role in ("user", "assistant")
    ]


# --------------------------------------------------
# Chat endpoint: RAG + Pi + PostgreSQL
# --------------------------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # 1. Retrieve relevant transcript passages.

        # 1. Load the existing conversation history.
        with SessionLocal() as db:
            session = db.get(ChatSession, session_id)

            if session is None:
                session = ChatSession(
                    session_id=session_id,
                    user_metadata={}
                )
                db.add(session)
                db.commit()

            history = load_history(db, session_id)

        # 2. Detect whether this is a follow-up question.
        is_follow_up = len(history) > 0

        # 3. Retrieve transcript passages for new conversations.
        sources = await retrieve_sources(request.message)

        # 4. Format retrieved transcript context.
        context = "\n\n".join(
            f"Source: {source['source']}\n"
            f"Passage: {source['text']}"
            for source in sources
        )

        if not is_follow_up and not sources:
            return {
                "reply": (
                    "I couldn't find relevant information "
                    "in the available transcripts."
                ),
                "sources": [],
                "model": CHAT_MODEL,
                "session_id": session_id
            }
        # 2. Format retrieved transcript context.
        context = "\n\n".join(
            f"Source: {source['source']}\n"
            f"Passage: {source['text']}"
            for source in sources
        )

        # 3. Create or retrieve the conversation session.
        with SessionLocal() as db:
            session = db.get(ChatSession, session_id)

            if session is None:
                session = ChatSession(
                    session_id=session_id,
                    user_metadata={}
                )
                db.add(session)
                db.commit()

            history = load_history(db, session_id)
            print("DEBUG HISTORY:", history)

        # 4. Format conversation history.
        history_text = "\n\n".join(
            f"{message['role'].upper()}:\n"
            f"{message['content']}"
            for message in history
        )

        # 5. Send context, history, and the current question to Pi.


        pi_prompt = (
            "You are Lenny Growth Assistant, an assistant that answers "
            "questions using Lenny's podcast and newsletter transcripts.\n\n"
            "IMPORTANT RULES:\n"
            "1. Read the conversation history carefully before answering.\n"
            "2. For follow-up questions, identify exactly what the user is "
            "referring to in the previous assistant answer.\n"
            "3. If the user asks for the second approach, identify the "
            "second approach explicitly listed or described in the previous "
            "assistant answer. Do not substitute another idea from the answer.\n"
            "4. If the user asks to summarize a previous answer, summarize "
            "only the relevant idea from that answer.\n"
            "5. Do not invent names, quotes, or claims.\n"
            "6. Treat transcript passages as evidence about Lenny's content. "
            "Do not claim a passage supports something it does not say.\n"
            "7. If the previous answer did not clearly list separate "
            "approaches, say that clearly rather than guessing.\n"
            "8. Keep the answer concise and direct.\n\n"
            f"CONVERSATION HISTORY:\n{history_text}\n\n"
            f"RETRIEVED TRANSCRIPT PASSAGES:\n{context}\n\n"
            f"CURRENT USER QUESTION:\n{request.message}"
        )

        reply = await ask_pi(pi_prompt)

        # 6. Prepare source references for the API response and database.
        source_records = [
            {
                "source": source["source"],
                "chunk": source["chunk"]
            }
            for source in sources
        ]

        # 7. Save the user message and assistant reply.
        with SessionLocal() as db:
            db.add_all([
                ChatMessage(
                    session_id=session_id,
                    role="user",
                    content=request.message,
                    sources=None
                ),
                ChatMessage(
                    session_id=session_id,
                    role="assistant",
                    content=reply,
                    sources=source_records
                )
            ])

            db.commit()

        # 8. Return the answer, sources, model, and session ID.
        return {
            "reply": reply,
            "sources": source_records,
            "model": CHAT_MODEL,
            "session_id": session_id
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not communicate with Ollama. "
                "Check that Ollama is running."
            )
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Database operation failed. "
                "Check the server logs."
            )
        ) from exc



# --------------------------------------------------
# Ship 30 for 30 writing endpoint
# --------------------------------------------------

@app.post("/write")
async def write_essay(request: WritingRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Please provide a topic for the essay."
        )

    try:
        sources = await retrieve_sources(topic)
        sources = sources[:4]

        context = "\n\n".join(
            f"Source: {source['source']}\n"
            f"Passage: {source['text']}"
            for source in sources
        )

        if not sources:
            raise HTTPException(
                status_code=404,
                detail="No relevant transcript passages found for this topic."
            )

        
        writing_prompt = (
            "You are an evidence-based essay writer creating a "
            "Ship 30 for 30 style essay using Lenny's podcast and "
            "newsletter transcript passages.\n\n"

            "TASK:\n"
            f"Write an insightful essay about: {topic}\n\n"

            "STRUCTURE:\n"
            "1. Start with a compelling, specific title.\n"
            "2. Open with a relatable problem or observation.\n"
            "3. State one clear central idea.\n"
            "4. Develop 4 to 6 sections with useful headings.\n"
            "5. Explain practical lessons and actionable steps.\n"
            "6. Include a concise, memorable conclusion.\n\n"

            "LENGTH AND STYLE:\n"
            "Aim for approximately 300 to 500 words. "
            "Use clear, natural language and original prose. "
            "Avoid repetition, generic filler, and exaggerated claims. "
            "Make the essay useful to startup founders and product teams.\n\n"

            "EVIDENCE AND ACCURACY RULES:\n"
            "- Treat the supplied passages as the only evidence "
            "for claims attributed to specific people.\n"
            "- Do not state a person's job title, company, or role unless "
            "the supplied passages explicitly confirm it. "
            "- Never invent names, job titles, company roles, statistics, "
            "quotes, or personal experiences.\n"
            "- Only use a direct quotation when the exact wording "
            "appears in the supplied passages.\n"
            "- If a speaker's role is not stated in the passages, "
            "use their name alone or describe the idea without attribution.\n"
            "- Do not present your own interpretation as a verified fact.\n"
            "- If the passages do not support a requested detail, "
            "leave it out rather than guessing.\n"
            "- Do not claim that every recommendation comes from a source.\n\n"

            "OUTPUT:\n"
            "Return only the finished essay in Markdown. "
            "Use a title and meaningful section headings. "
            "Do not include a preamble explaining your process.\n\n"

            f"TOPIC:\n{topic}\n\n"
            f"RESEARCH PASSAGES:\n{context}\n"
        )

        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": CHAT_MODEL,
                    "prompt": writing_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 600
                    }
                }
            )
            response.raise_for_status()
            essay = response.json()["response"].strip()

        return {
            "topic": topic,
            "essay": essay,
            "sources": [
                {
                    "source": source["source"],
                    "chunk": source["chunk"]
                }
                for source in sources
            ],
            "model": CHAT_MODEL
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not communicate with the local AI model."
        ) from exc