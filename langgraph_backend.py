from langgraph.graph import StateGraph ,START ,END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage , SystemMessage ,HumanMessage
from langgraph.checkpoint.memory import InMemorySaver   
import re


load_dotenv()


from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


config={"configurable":{"thread_id":"1"}}

model=ChatGroq(model="qwen/qwen3-32b", reasoning_format="hidden")

def chat_node(state:ChatState):

    messages = state["messages"]

    response = model.invoke(messages)

    return {"messages":[response]}





checkpointer=InMemorySaver()

graph=StateGraph(ChatState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)


Chatbot=graph.compile(checkpointer=checkpointer)




 
for chunk, metadata in Chatbot.stream(
    {'messages':[HumanMessage(content="write 500 words. essage on ai ")]},
    config=config,
    stream_mode="messages"
):
     if chunk.content:
        print(chunk.content, end=" ", flush=True)




