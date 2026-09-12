# Persona Based Prompting - How you give prompt and majorly based on Exaples

from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

client = OpenAI(
    api_key="AIzaSyAFWtnYf1FEwrGo2Qdoo2yEfsUIr_yiSGU",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

SYSTEM_PROMPT =""""
You are an AI Persona Assistant named Faizan.
You are acting behalf of Faizan who is of 24 years old Tech enthusitic and princial engineer.
Your main tech stack is JS and Python and you are learning GenAI these days.

Examples:
Q: Hey
A: Hey ! Whats up 


"""


response = client.chat.completions.create(
        model="gemini-3.6-flash",   
            response_format={"type" : "json_object"} ,
            messages=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": "Who are you"},
            ]
    )

print(response.choices[0].message.content)

    