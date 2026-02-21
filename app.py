import json

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from db import init_db
from memory import Memory
from llm.client import chat
from llm.prompt import SYSTEM_PROMPT
#from rag.retriever import retrieve
from rag.pipeline import rag

app = FastAPI()

from db import get_db

@app.get("/sessions")
def get_sessions():
    db = get_db()
    rows = db.execute("""
        SELECT id,title
        FROM sessions
        ORDER BY created_at DESC
    """).fetchall()

    return [dict(r) for r  in rows]

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):

    db = get_db()

    db.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    db.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    db.commit()

    return {"status": "ok"}


@app.on_event("startup")
def start():
    init_db()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: str = "openai"
    images: Optional[List[dict]] = None


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/history/{session_id}")
def history(session_id: str):
    m = Memory(session_id, SYSTEM_PROMPT)
    return {"messages": m.history()}


ANALYSIS_PROMPT = (
    "You are a failure-analysis assistant. Analyze the investigation conversation and "
    "return ONLY a valid JSON object (no markdown fences, no extra text) with these fields:\n"
    '- "issue_name": brief issue title (5 words max)\n'
    '- "root_causes": array of 2-6 short root cause hypotheses (3-8 words each)\n'
    '- "root_cause_summary": detailed paragraph summarizing root cause analysis so far\n'
    '- "corrective_actions": detailed paragraph of recommended corrective actions\n'
    "Respond in the same language as the conversation."
)


@app.get("/analyze/{session_id}")
def analyze_session(session_id: str):
    mem = Memory(session_id, SYSTEM_PROMPT)
    history = mem.history()

    user_msgs = [m for m in history if m["role"] == "user"]
    if not user_msgs:
        return {
            "issue_name": "",
            "root_causes": [],
            "root_cause_summary": "",
            "corrective_actions": "",
        }

    conversation_text = "\n".join(
        f'{m["role"]}: {m["content"]}'
        for m in history if m["role"] != "system"
    )

    raw = chat([
        {"role": "system", "content": ANALYSIS_PROMPT},
        {"role": "user", "content": conversation_text},
    ])

    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text[:-3].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "issue_name": "Analysis Pending",
            "root_causes": [],
            "root_cause_summary": raw,
            "corrective_actions": "",
        }

    return data


def build_messages_with_images(message: str, images: Optional[List[dict]] = None):
    """Build messages array with image support for OpenAI/Gemini"""
    if not images or len(images) == 0:
        return [{"role": "user", "content": message}]
    
    # For OpenAI format with images
    content = [{"type": "text", "text": message}]
    for img in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img['mime_type']};base64,{img['data']}"
            }
        })
    
    return [{"role": "user", "content": content}]


@app.post("/chat")
async def chat_api(body: ChatRequest):
    session_id = body.session_id
    message = body.message
    provider = body.provider
    image_data = body.images
    mem = Memory(session_id, SYSTEM_PROMPT)

    context, confidence = rag(message)

    # Build user message with images
    if image_data:
        user_messages = build_messages_with_images(message, image_data)
    else:
        user_messages = [{"role": "user", "content": message}]

    # ---------- RAG HIT ----------
    if context:
        print("RAG HIT")

        user_prompt = f"""
Answer the question using ONLY the sources below.

Sources:
{context}

Question:
{message}
"""

        # Build messages for LLM call
        if image_data:
            # Include images in the message
            messages_for_llm = [{"role": "system", "content": SYSTEM_PROMPT}]
            content = [{"type": "text", "text": user_prompt}]
            for img in image_data:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{img['mime_type']};base64,{img['data']}"
                    }
                })
            messages_for_llm.append({"role": "user", "content": content})
        else:
            messages_for_llm = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]

        # Store text-only version in memory
        mem.add("user", user_prompt)

        reply = chat(messages_for_llm, provider=provider)

        mem.add("assistant", reply)
        mem.maybe_title()

        return {
            "reply": reply,
            "confidence": round(confidence, 2)
        }

    # ---------- RAG MISS ----------
    else:
        print("RAG MISS → fallback")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if image_data:
            messages.extend(build_messages_with_images(message, image_data))
        else:
            messages.append({"role": "user", "content": message})

        reply = chat(messages, provider=provider)

        # Store text-only version in memory
        mem.add("user", message)
        mem.add("assistant", reply)
        mem.maybe_title()

        return {
            "reply": reply,
            "confidence": round(confidence, 2)
        }
