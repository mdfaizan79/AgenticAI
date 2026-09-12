# Reterival phase

from dotenv import load_dotenv
from pathlib import Path
from google import genai
from openai import OpenAI
import os
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

openai_client = OpenAI( api_key=os.getenv("OPENAI_API_KEY") )

# Vector Embedding 

embedding_model =OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model

)

# Take User Input

user_query=input("Ask Something : ")

# Return relevent chunks from db

search_result =vector_db.similarity_search(query=user_query)

context = "\n\n".join(
    [
        f"Page Content: {result.page_content}\n"
        f"Page Number: {result.metadata['page_label']}\n"
        f"File Location: {result.metadata['source']}"
        for result in search_result
    ]
)

SYSTEM_PROMPT="""" 
You are AI assistance which will give user query response based on available context retrieved  from a pdf along with page_contents and page_number.

You should only answer the user based on the following context and navigate the user to open
the right page number to know more
"""

response= openai_client.chat.completions.create(
    model="gpt-5",
    message=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role":"user", "content": user_query},

    ]
)

print(f"👽:{response.choices[0].message.content}")