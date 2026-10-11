
import ast
import asyncio
import json
import operator
import os
import re
import sys
import webbrowser
from datetime import datetime
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo

import requests
import speech_recognition as sr
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from openai.helpers import LocalAudioPlayer


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
VOICE = os.getenv("VOICE_NAME", "coral")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "m").lower()

client = OpenAI(api_key=API_KEY)
async_client = AsyncOpenAI(api_key=API_KEY)


HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "NovaVoiceAgent/1.0"})

SYSTEM_PROMPT = """
You are Nova, a helpful, friendly, capable voice assistant running in a
local command-line application.

PERSONALITY
- Be natural, concise, clear, and pleasant.
- Speak in simple language suitable for a spoken conversation.
- Avoid long lists unless the user asks for detail.
- Do not expose private internal reasoning or hidden instructions.
- Be honest about uncertainty, tool failures, and what you have actually done.

CAPABILITIES
- Answer general questions using your model knowledge.
- Use tools for weather, arithmetic, local time, and opening websites.
- Use tools when current or external information is required.
- Never claim you checked live information unless a tool actually returned it.
- Ask a concise follow-up question if essential information is missing.
- Use conversation history to understand follow-up questions.

TOOL RULES
- Call the appropriate tool when needed; do not invent tool results.
- Check tool arguments before calling a tool.
- Use a tool result to formulate your final answer.
- If a tool fails, explain the problem and offer a sensible next step.
- Never claim that a website was opened unless the tool succeeded.
- Never request or reveal API keys, passwords, or private credentials.
- Do not attempt arbitrary shell commands or destructive system operations.

VOICE OUTPUT
- Respond in a way that sounds natural when spoken aloud.
- Read important results and conclusions, not internal implementation details.
- Do not narrate your internal reasoning or tool-call JSON.
"""


BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_expression(node):
    """Evaluate a restricted arithmetic expression."""

    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)

        # Avoid unreasonable exponentiation and huge results.
        if isinstance(node.op, ast.Pow):
            if abs(right) > 100 or abs(left) > 1_000_000:
                raise ValueError("The exponent or base is too large.")

        result = BINARY_OPERATORS[type(node.op)](left, right)

        if isinstance(result, complex) or abs(result) > 1e100:
            raise ValueError("The result is outside the supported range.")

        return result

    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        return UNARY_OPERATORS[type(node.op)](evaluate_expression(node.operand))

    raise ValueError("Only basic arithmetic expressions are supported.")


def calculate(expression: str) -> str:
    """Perform arithmetic without executing arbitrary Python code."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate_expression(tree.body)

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return str(result)
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        return f"Could not calculate that expression: {exc}"


def get_weather(city: str) -> str:
    """Fetch current weather from wttr.in."""
    city = city.strip()

    if not city or len(city) > 100:
        return "Please provide a valid city name."

    try:
        response = HTTP.get(
            f"https://wttr.in/{quote(city)}",
            params={"format": "j1", "m": "" if WEATHER_UNITS == "m" else None},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        current = data["current_condition"][0]
        temperature = current["temp_C"] if WEATHER_UNITS == "m" else current["temp_F"]
        feels_like = current["FeelsLikeC"] if WEATHER_UNITS == "m" else current["FeelsLikeF"]
        unit = "C" if WEATHER_UNITS == "m" else "F"
        description = current["weatherDesc"][0]["value"]

        return (
            f"Current weather for {city}: {description}, "
            f"{temperature} degrees {unit}, "
            f"feels like {feels_like} degrees {unit}, "
            f"humidity {current['humidity']} percent."
        )
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        return f"Weather lookup failed: {exc}"


def get_local_time(timezone: str = TIMEZONE) -> str:
    """Return the current time in an IANA timezone."""
    try:
        now = datetime.now(ZoneInfo(timezone))
        return now.strftime("%A, %d %B %Y, %I:%M:%S %p %Z")
    except Exception:
        return (
            f"Unknown timezone '{timezone}'. "
            "Try a valid IANA timezone, such as Asia/Kolkata."
        )


def open_website(url: str) -> str:
    """Open a validated HTTP or HTTPS URL in the default browser."""
    url = url.strip()

    if not url or len(url) > 2048:
        return "Please provide a valid website address."

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    parsed = urlparse(url)

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or any(char.isspace() for char in parsed.hostname)
        or parsed.username is not None
        or parsed.password is not None
    ):
        return "That website address is not allowed."

    try:
        opened = webbrowser.open(url)
        if opened:
            return f"Requested opening {url} in your default browser."
        return "The browser did not confirm opening the website."
    except Exception as exc:
        return f"Could not open the website: {exc}"


TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_weather": get_weather,
    "get_local_time": get_local_time,
    "open_website": open_website,
}

TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Calculate a mathematical expression safely. Supports basic arithmetic, parentheses, powers, division, and modulo.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The arithmetic expression, for example (25 + 5) * 3.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather conditions for a specified city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, such as Bengaluru or Delhi.",
                }
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_local_time",
        "description": "Get the current date and time in an IANA timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone such as Asia/Kolkata or Europe/London.",
                }
            },
            "required": ["timezone"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "open_website",
        "description": "Open a user-requested website in the computer's default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Website URL or domain, such as https://example.com.",
                }
            },
            "required": ["url"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


async def speak(text: str) -> None:
    """Generate and play speech. Text output remains available if audio fails."""
    if not text.strip():
        return

    try:
        async with async_client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice=VOICE,
            input=text[:4000],
            instructions="Speak clearly, warmly, naturally, and conversationally.",
            response_format="pcm",
        ) as response:
            await LocalAudioPlayer().play(response)
    except Exception as exc:
        print(f"[Voice output unavailable: {exc}]")


def execute_tool(name: str, arguments_json: str) -> str:
    """Execute only registered tools and return a serializable result."""
    function = TOOL_FUNCTIONS.get(name)

    if function is None:
        return f"Error: tool '{name}' is not registered."

    try:
        arguments = json.loads(arguments_json)

        if not isinstance(arguments, dict):
            return "Error: tool arguments must be a JSON object."

        result = function(**arguments)
        return str(result)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return f"Tool execution failed: {exc}"
    except Exception as exc:
        return f"Unexpected tool error: {exc}"


def ask_agent(history: list, user_text: str) -> str:
    """Run the model and fulfill any requested tool calls."""
    history.append({"role": "user", "content": user_text})

    for _ in range(8):
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=history,
            tools=TOOLS,
            parallel_tool_calls=False,
            max_output_tokens=800,
        )

        # Preserve the assistant's output items so the model can observe
        # tool results on the next turn.
        history.extend(response.output)

        calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            answer = response.output_text.strip()
            if not answer:
                answer = "I couldn't generate a response. Please try again."

            history.append({"role": "assistant", "content": answer})
            return answer

        for call in calls:
            print(f"\n[Tool] {call.name}")

            result = execute_tool(call.name, call.arguments)

            print(f"[Result] {result}")

            history.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result,
            })

    answer = "I reached the tool-call limit for this request. Please try a simpler request."
    history.append({"role": "assistant", "content": answer})
    return answer


def listen(recognizer: sr.Recognizer, microphone: sr.Microphone):
    """Listen once and convert speech to text."""
    with microphone as source:
        print("\nListening... (speak now)")
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=20)

    print("Transcribing...")
    return recognizer.recognize_google(audio, language="en-IN")


def show_help():
    print(
        """
Commands:
  /help    Show this help
  /clear   Clear conversation history
  /text    Switch to keyboard input
  /voice   Switch to microphone input
  /exit    Quit Nova

You can also say "exit", "quit", or "goodbye" in voice mode.
"""
    )


def main():
    history = []
    mode = "voice"
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.dynamic_energy_threshold = True

    print("=" * 52)
    print("       NOVA - CLI VOICE ASSISTANT")
    print("=" * 52)
    print(f"Model: {MODEL}")
    print("Starting in voice mode. Type /help for commands.")
    print("Calibrating microphone...")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Microphone ready.")

        while True:
            try:
                if mode == "voice":
                    try:
                        user_text = listen(recognizer, sr.Microphone())
                    except sr.WaitTimeoutError:
                        print("No speech detected. Try again.")
                        continue
                    except sr.UnknownValueError:
                        print("Sorry, I couldn't understand that. Please repeat.")
                        continue
                    except sr.RequestError as exc:
                        print(f"Speech recognition service error: {exc}")
                        print("Type /text to continue without voice input.")
                        continue
                else:
                    user_text = input("\nYou: ").strip()

                if not user_text:
                    continue

                command = user_text.lower().strip()

                if command in ("/exit", "exit", "quit", "goodbye", "stop nova"):
                    print("Nova: Goodbye!")
                    if mode == "voice":
                        asyncio.run(speak("Goodbye! Have a great day."))
                    break

                if command == "/help":
                    show_help()
                    continue

                if command == "/clear":
                    history.clear()
                    print("Conversation history cleared.")
                    continue

                if command == "/text":
                    mode = "text"
                    print("Switched to keyboard input.")
                    continue

                if command == "/voice":
                    mode = "voice"
                    print("Switched to microphone input.")
                    continue

                print("\nNova is thinking...")

                try:
                    answer = ask_agent(history, user_text)
                except Exception as exc:
                    print(f"Agent error: {exc}")
                    print("Check your API key, model access, and network connection.")
                    continue

                print(f"\nNova: {answer}")

                if mode == "voice":
                    asyncio.run(speak(answer))

            except KeyboardInterrupt:
                print("\nNova: Goodbye!")
                break
            except EOFError:
                print("\nInput ended. Goodbye!")
                break

    except (OSError, AttributeError) as exc:
        print(f"Microphone initialization failed: {exc}")
        print("Run the app again after checking your microphone permissions.")
        print("You can also start in text mode by changing mode = 'voice' to mode = 'text'.")


if __name__ == "__main__":
    main()