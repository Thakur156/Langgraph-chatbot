from langgraph.graph import StateGraph ,START ,END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage , SystemMessage ,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver   
import re

import sqlite3


load_dotenv()


from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]




model=ChatGroq(model="qwen/qwen3-32b", reasoning_format="hidden")

def chat_node(state:ChatState):

    messages = state["messages"]

    response = model.invoke(messages)

    return {"messages":[response]}



conn= sqlite3.connect(database='Chatbot.db',check_same_thread=False)

checkpointer=SqliteSaver(conn=conn)

graph=StateGraph(ChatState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)


Chatbot=graph.compile(checkpointer=checkpointer)


def retreive_all_threads():

    all_threads=set()

    for checkpoint in checkpointer.list(None):
       all_threads.add(checkpoint.config["configurable"]['thread_id'])
    
    return list(all_threads)











# config={"configurable":{"thread_id":"1"}}

# #test


# response= Chatbot.invoke(
#     {'messages':[HumanMessage(content='whats is my name')]},
#         config=config,
#     )


# print (response)