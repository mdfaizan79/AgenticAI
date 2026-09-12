from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

text = "Effel Tower is in Parish and it is famous landmark, it is 324 meters tall"

response = client.embeddings.create(
    input=text,
    model="text-embedding-3-large"
)
print("Vector Embedding: ",response.data[0].embedding)