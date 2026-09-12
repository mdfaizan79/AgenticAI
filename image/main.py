from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[
        {
            "role":"user",
            "content": [
                {"type":"text" ,"text":"generate the caption for this image in about 20 words"},
                {"type":"image_url", "image_url":{"url":"https://images.pexels.com/photos/39332580/pexels-photo-39332580.jpeg"}}
            ]
        }
    ]
)

print("Response:",response.choices[0].message.content)