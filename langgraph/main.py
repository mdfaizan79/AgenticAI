from typing_extensions import TypedDict 
from typing import Annotated
from langgraph.graph.message import add_message
from langgraph.graph import StateGraph

import operator


class State(TypedDict):
    messages:Annotated[list,add_message]

def chatbot(state:State):

    return {"message":["hi, This is the message from chatbot"]}

def samplenode(state:State):

    return {"message":["Sample message Appended"]}

graph_builder = StateGraph()

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("samplenode",samplenode)

# state = {message:["Hey there"]}
# node runs: chatbot(state:["Hey there"]) -> This is the message from chatbot
# state = {message:["Hey there",Hi This is the message from chatbot Node]}