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
    model="gemini-3.6-flash",   
    messages=[
        {"role": "user", "content": "You are an Expert in mathematics, so give the response related  to only mathematics. If it is not realted to mathematics then say Sorry I Cannot respond to this"
        ""},
        {"role":"user", "content":" give the formula for a + b whole square"}
    ]
)

print(result.choices[0].message.content)
