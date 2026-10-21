import asyncio
import io
import json
from pathlib import Path

import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import voice_agent as va

app = FastAPI(title="Alexa AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


SESSIONS: dict[str, list] = {}  # Conversation history per browser session

VOICES = {
    "alloy", "ash", "ballad", "coral", "echo",
    "fable", "nova", "onyx", "sage", "shimmer"
}


@app.get("/api/health")
def health():
    return {"ok": True, "model": va.MODEL, "tts_model": va.TTS_MODEL,
            "voice": va.VOICE, "has_key": bool(va.API_KEY)}


def transcribe(wav: bytes, language: str) -> str:
    """Google Speech Recognition on the WAV recorded in the browser."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language=language)


def tool_events(items):
    names = {}
    for it in items:
        get = (lambda k, it=it: it.get(k)) if isinstance(it, dict) else (lambda k, it=it: getattr(it, k, None))
        kind = get("type")
        if kind == "function_call":
            names[get("call_id")] = (get("name"), get("arguments"))
        elif kind == "function_call_output":
            name, args = names.get(get("call_id"), ("tool", ""))
            yield {"name": name, "arguments": args, "result": get("output")}



async def emit(ws: WebSocket, type_: str, **data):
    await ws.send_text(
        json.dumps({"type": type_, **data})
    )




async def run_turn(ws: WebSocket, history: list, text: str, cfg: dict):
    await emit(ws, "user", text=text)
    await emit(ws, "state", state="thinking")

    start = len(history)

    try:
        answer = await asyncio.to_thread(
            va.ask_agent, history, text
        )
    except Exception as exc:
        await emit(
            ws,
            "error",
            message=f"Agent error: {exc}. Check your API key, model access, and network connection."
        )
        await emit(ws, "state", state="idle")
        return

    for event in tool_events(history[start:]):
        await emit(ws, "tool", **event)

    await emit(ws, "assistant", text=answer)

    if cfg["speak"]:
        try:
            audio = await va.synthesize(answer, cfg["voice"])
            await ws.send_bytes(audio)
            return
        except Exception as exc:
            await emit(
                ws,
                "error",
                message=f"Voice output unavailable: {exc}"
            )

    await emit(ws, "state", state="idle")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, session: str = "default"):
    await ws.accept()
    history = SESSIONS.setdefault(session, [])
    cfg = {"voice": va.VOICE, "speak": True, "language": "en-IN"}
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg.get("bytes"):  # microphone audio (16 kHz mono WAV)
                await emit(ws, "state", state="thinking")
                try:
                    text = await asyncio.to_thread(transcribe, msg["bytes"], cfg["language"])
                except sr.UnknownValueError:
                    await emit(ws, "error", message="Sorry, I couldn't understand that. Please repeat.")
                    continue
                except sr.RequestError as exc:
                    await emit(ws, "error", message=f"Speech recognition service error: {exc}. Try typing instead.")
                    continue
                except Exception as exc:
                    await emit(ws, "error", message=f"Could not read the audio: {exc}")
                    continue
                await run_turn(ws, history, text, cfg)
            elif msg.get("text"):
                try:
                    data = json.loads(msg["text"])
                except json.JSONDecodeError:
                    continue
                kind = data.get("type")
                if kind == "text" and str(data.get("text", "")).strip():
                    await run_turn(ws, history, str(data["text"]).strip()[:2000], cfg)
                elif kind == "clear":
                    history.clear()
                    await emit(ws, "cleared")
                    await emit(ws, "state", state="idle")
                elif kind == "config":
                    if data.get("voice") in VOICES:
                        cfg["voice"] = data["voice"]
                    if isinstance(data.get("speak"), bool):
                        cfg["speak"] = data["speak"]
                    if isinstance(data.get("language"), str) and len(data["language"]) <= 8:
                        cfg["language"] = data["language"]
    except WebSocketDisconnect:
        pass


DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.exists():  # after `npm run build`, FastAPI serves the site on one port
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
