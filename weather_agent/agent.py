from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import os
import json
import requests
from pydantic import BaseModel , Field
from typing import Optional


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)
def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response= requests.get(url)

    if response.status_code == 200 :
        return f"The weather {city} is {response.text}"
    
    return "Something Went Wrong😔"

available_tool={
        "get_weather" : get_weather
}

SYSTEM_PROMPT =""""
You are an expert AI Assistance in resolving user queries using chain of thought
You work on START , PLAN and OUTPUT steps.
You need to plan first what is needed to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done ,then finally give an OUTPUT.
For every tool call wait for observe step which is the output from the called tool. 

RULES:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The Sequence of steps is START (where user give the input), PLAN (They can
  be multiple times) and finally OUTPUT(which is going to display to the user).

OUTPUT JSON formate :
{"step": "START" | "PLAN" | "OUTPUT" | "TOOL" , "content" : "string" ,"tool" :"string","input":"string"}

Example 1:
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

Example 2:
START : What is the Weather in Delhi ?
PLAN : {"step" : "PLAN" : "content" : "seems like user in intrested in sknowing the weather in   Delhi in India"}
PLAN : {"step" : "PLAN" : "content" : "Let see if we have avilable tool from the list that give the weather update "}
PLAN : {"step" : "PLAN" : "content" : "Great ! , we have get_weather tool avilable for this query"}
PLAN : {"step" : "PLAN" : "content" : "For this I need to call get_weather tool for delhi as input for city"}
PLAN : {"step" : "TOOL" : "tool" : "get_weather, "input" :"delhi"}
PLAN : {"step" : "OBSERVE" : "tool" : "get_weather, "Output" : "The temp of delhi is cloudy with  20 C"}
PLAN : {"step" : "PLAN" : "content" : ""}
PLAN : {"step" : "PLAN" : "content" : "Great,I got the weather of delhi"}
OUTPUT : {"step" : "OUTPUT" : "content" : "The Weather of delhi is 20 C with some Cloudy sky"}

"""

print("\n\n\n")

class MyOutputFormat(BaseModel):
        step: str = Field(...,description="The ID of the step.Example:PLAN,OUTPUT,TOOL,etc")
        content:Optional[str] = Field(None,description="The optional string content for the step")
        tool:Optional[str] = Field(None,description="The ID of the tool to call")
        input:Optional[str] = Field(None,description="The input params for the tool")

message_history=[
    {"role":"system","content": SYSTEM_PROMPT},
]

while True:        
 user_query = input("👉🏻")
 message_history.append({"role":"user","content":user_query})

 while True:
    response = client.chat.completions.parse(
        model="gemini-3.6-flash", 
            response_format=MyOutputFormat ,
            messages=message_history
    )
    raw_result= (response.choices[0].message.content)
    message_history.append({"role":"user" , "content" : raw_result} )
    parse_result= response.choices[0].message.parsed

    if parse_result.step== "START":
                        print(type(parse_result))
                        print(parse_result)
                        #print("💁🏻",parse_result.get("content"))
                        continue
    if parse_result.step== "TOOL":
                            tool_to_call=parse_result.tool
                            tool_input=parse_result.input
                            print(f"🛠️:{tool_to_call}({tool_input})")

                            tool_response = available_tool[tool_to_call](tool_input)
                            print(f"🛠️:{tool_to_call}({tool_input}) ={tool_response}")
                            message_history.append({"role":"developer","content":json.dumps(
                                    {"step":"OBSERVE","tool":tool_to_call,"input":tool_input,"output":tool_response}
                            )})
                            continue
    if parse_result.step== "PLAN":
                            print("📡",parse_result.content)
                            continue
    if parse_result.step== "OUTPUT":
                                print("😍",parse_result.content)
                                break



print("\n\n\n")
