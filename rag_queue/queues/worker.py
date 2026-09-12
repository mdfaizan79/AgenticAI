from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

openai_client =OpenAI()

# Vector Embedding 

embedding_model =OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model

)

def process_query(query:str):
    print("Searching chuncks",query)

    search_result =vector_db.similarity_search(query=query)

    context = "\n\n".join(
        [
        f"Page Content: {result.page_content}\n"
        f"Page Number: {result.metadata['page_label']}\n"
        f"File Location: {result.metadata['source']}"
        for result in search_result
        ]
)

    SYSTEM_PROMPT=f""" 
    You are AI assistance which will give user query response based on available context retrieved  from a pdf along with page_contents and page_number.

    You should only answer the user based on the following context and navigate the user to open
    the right page number to know more.

    Context:
    {context}
    """

    response = openai_client.responses.create(
    model="gpt-5.6-luna",
    reasoning={"effort": "medium"},
    input=[
        {
            "role": "system",
            "content": "Answer the user's question using the provided context."
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{query}"
        }
    ]
)

    answer = response.choices[0].message.content

    print(f"👽: {answer}")

    return answer