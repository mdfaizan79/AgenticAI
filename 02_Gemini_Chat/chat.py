from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI()

print("API KEY from .env:", os.getenv("OPENAI_API_KEY"))

result = client.chat.completions.create(
    model="gpt-4o-mini",   # or "gpt-4" if you have access
    messages=[
        {"role": "user", "content": "Hey , I am Faizan"}
    ]
)

print(result.choices[0].message.content)
