
import os
import json
import asyncio
import requests
import speech_recognition as sr

from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from openai.helpers import LocalAudioPlayer


# --------------------------------------------------
# 1. INITIALIZATION
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Add it to your .env file."
    )

client = OpenAI(api_key=api_key)
async_client = AsyncOpenAI(api_key=api_key)

CHAT_MODEL = "gpt-4.1"
TTS_MODEL = "gpt-4o-mini-tts"
VOICE = "coral"

MAX_TOOL_ROUNDS = 8
MAX_HISTORY_MESSAGES = 30


# --------------------------------------------------
# 2. SYSTEM PROMPT
# --------------------------------------------------
