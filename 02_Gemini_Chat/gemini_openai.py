from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key="AIzaSyAFWtnYf1FEwrGo2Qdoo2yEfsUIr_yiSGU",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

print("API KEY from .env:", os.getenv("OPENAI_API_KEY"))

result = client.chat.completions.create(
    model="gemini-3.6-flash",   # or "gpt-4" if you have access
    messages=[
        {"role": "user", "content": "Hey , I am Faizan. and Who are you"
        ""}
    ]
)

print(result.choices[0].message.content)
