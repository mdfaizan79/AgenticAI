from openai import OpenAI
from google import genai
from dotenv import load_dotenv
import requests

load_dotenv()

client = OpenAI(
    api_key="AIzaSyAFWtnYf1FEwrGo2Qdoo2yEfsUIr_yiSGU",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response= requests.get(url)

    if response.status_code == 200 :
        return f"The weather {city} is {response.text}"
    
    return "Something Went Wrong😔"

def main():
    user_query =input("> ")
    response = client.chat.completions.create(
        model="gemini-3.6-flash", 
        messages=[
            {"role":"user" , "content" : user_query}
        ]
    )

    print(f"📡: {response.choices[0].message.content}") 

#main()

print(get_weather("Delhi"))