from dotenv import load_dotenv
from typing_extensions import TypedDict 
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START,END


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

def samplenode(state:State):
    print("\n\n Inside samplenode node", state)
    return {"messages":["Sample message Appended"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("samplenode",samplenode)

# state = {message:["Hey there"]}
# node runs: chatbot(state:["Hey there"]) -> This is the message from chatbot
# state = {message:["Hey there",Hi This is the message from chatbot Node]}

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

# (START) -> chatbot -> samplenode -> (END)

graph = graph_builder.compile()

update_state = graph.invoke(State({"messages":["Hi,My Name is Md Faizan"]}))
print("\n\n update_state",update_state)


