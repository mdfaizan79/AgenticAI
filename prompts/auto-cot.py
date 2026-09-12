# Chain-Of-Thought Prompting

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
You are an expert AI Assistance in resolving user queries using chain of thought
You work on START , PLAN and OUTPUT steps.
You need to plan first what is needed to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done ,then finally give an OUTPUT.

RULES:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The Sequence of steps is START (where user give the input), PLAN (They can
  be multiple times) and finally OUTPUT(which is going to display to the user).

OUTPUT JSON formate :
{"step": "START" | "PLAN" | "OUTPUT" , "content" : "string"}

Example:
START : Hey can you solve 2 + 3 * 5 / 10
PLAN : {"step" : "PLAN" : "content" : "seems like user in intrested in solving math problem"}
PLAN : {"step" : "PLAN" : "content" : "Look at the problem, we should solve using BODMAS methods"}
PLAN : {"step" : "PLAN" : "content" : "Yes, BODMAS  is correct approach to solve this problem"}
PLAN : {"step" : "PLAN" : "content" : "First multiply 3 * 5 which gives 15"}
PLAN : {"step" : "PLAN" : "content" : "So , Now new equation become 2 + 15 / 10"}
PLAN : {"step" : "PLAN" : "content" : "So , Now we do divide operation 15/10 = 1.5"}
PLAN : {"step" : "PLAN" : "content" : "So , Now new equation become 2 + 1.5"}
PLAN : {"step" : "PLAN" : "content" : "So , Now finally lets perform the addition 2 + 1.5 = 3.5"}
PLAN : {"step" : "PLAN" : "content" : "Great,we have solve this and finally left with 3.5 as Ans"}
OUTPUT : {"step" : "OUTPUT" : "content" : "3.5"}

"""

print("\n\n\n")

message_history=[
    {"role":"system","content": SYSTEM_PROMPT},
]

user_query = input("👉🏻")
message_history.append({"role":"user","content":user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-3.6-flash", 
            response_format={"type" : "json_object"} ,
            messages=message_history
    )
    raw_result= (response.choices[0].message.content)
    message_history.append({"role":"user" , "content" : raw_result} )
    parse_result= json.loads(raw_result)

    if parse_result.get("step" )== "START":
                        print("💁🏻",parse_result.get("content"))
                        continue
    if parse_result.get("step" )== "PLAN":
                            print("🙈",parse_result.get("content"))
                            continue
    if parse_result.get("step" )== "OUTPUT":
                                print("😍",parse_result.get("content"))
                                break



print("\n\n\n")
