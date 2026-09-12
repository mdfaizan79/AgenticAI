from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key="AIzaSyAFWtnYf1FEwrGo2Qdoo2yEfsUIr_yiSGU",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

SYSTEM_PROMPT =""""
You are Ali . You will answer only the questions related to coding, If it is not related to coding then say SORRY .

Examples :-
Q: What is the a + b whole square ?
A: Sorry 

Q: Who is The PM of India?
A: Sorry

Q: Write python code to add two number
A: def addnum(a,b)
    return (a+b)

"""



result = client.chat.completions.create(
    model="gemini-3.6-flash",   
    messages=[
        {"role": "user", "content": SYSTEM_PROMPT},
        {"role":"user", "content":" give me the python code for translating the sentences in hindi"}
    ]
)

print(result.choices[0].message.content)
