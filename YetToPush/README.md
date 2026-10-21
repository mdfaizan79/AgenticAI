# Alexa AI

React + Vite + Tailwind + Framer Motion front end, FastAPI back end wrapping your existing agent (`backend/voice_agent.py`).

## How it works
- Browser mic -> recorded as 16 kHz WAV -> WebSocket `/ws` -> Google Speech Recognition (`speech_recognition`) -> your `ask_agent()` (history + `open_website` tool intact) -> OpenAI TTS (MP3) -> WebSocket -> browser plays it.
- Orb and waveform are driven by Web Audio `AnalyserNode` data (your mic while listening, Alexa's voice while speaking). States come from backend events.
- Conversation history is kept per browser session on the server (in memory); `Clear conversation` resets it.
- API keys stay in `backend/.env`; the frontend never sees them.

## Run (development)
```bash
# terminal 1
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
test -f .env || cp ../.env.example .env               # add OPENAI_API_KEY
uvicorn main:app --reload --port 8000

# terminal 2
cd frontend
npm install
npm run dev                                           # http://localhost:5173
```

## Run (single port)
`cd frontend && npm run build`, then start uvicorn: the site is served at http://localhost:8000.

## Notes
- Use `localhost` or HTTPS: browsers only allow the microphone on secure origins. Chrome/Edge/Safari recommended.
- `open_website` opens the page in the browser of the machine running the backend (fine for local use).
- Google Speech Recognition uses the free web endpoint, so it needs internet access.
