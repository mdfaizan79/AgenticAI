from dotenv import load_dotenv
from typing_extensions import TypedDict 
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.mongodb import MongoDBSaver


import operator

load_dotenv()

llm =init_chat_model(
    model="gpt-5.6-luna",
    model_provider="openai"
)

class State(TypedDict):
    messages:Annotated[list,add_messages]

def chatbot(state:State):
    response =llm.invoke(state.get("messages"))
    return {"messages":[response]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)


# state = {message:["Hey there"]}
# node runs: chatbot(state:["Hey there"]) -> This is the message from chatbot
# state = {message:["Hey there",Hi This is the message from chatbot Node]}

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)

# (START) -> chatbot -> samplenode -> (END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URL = "mongodb://localhost:27017"
with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
    

    config = {
            "configurable":{
                "thread_id": "faizan"
            }
        }

    update_state = graph_with_checkpointer.invoke(
    State({"messages":["What is my name"]}),
    config,
    )
print("\n\n update_state",update_state)

# Checkpointer (piyush) = Hey, My name is Md Faizan


