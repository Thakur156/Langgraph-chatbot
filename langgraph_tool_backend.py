from langgraph.graph import StateGraph ,START ,END
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage , SystemMessage ,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver   
import re
import requests
import os

import sqlite3


load_dotenv()


from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


model=ChatGroq(model="qwen/qwen3-32b", reasoning_format="hidden")


# -------------------
# 2. Tools
# -------------------
# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}
    

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {"error": "Missing ALPHA_VANTAGE_API_KEY in environment variables"}

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url, timeout=15)
    return r.json()



tools= [search_tool,get_stock_price,calculator]

llm_with_tools= model.bind_tools(tools)


tool_node= ToolNode(tools)

def chat_node(state:ChatState):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {"messages":[response]}



conn= sqlite3.connect(database='Chatbot.db',check_same_thread=False)

checkpointer=SqliteSaver(conn=conn)

graph=StateGraph(ChatState)

graph.add_node("chat_node",chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {"tools": "tools", "__end__": END},
)
graph.add_edge("tools","chat_node")


Chatbot=graph.compile(checkpointer=checkpointer)


def retreive_all_threads():

    all_threads=set()

    for checkpoint in checkpointer.list(None):
       all_threads.add(checkpoint.config["configurable"]['thread_id'])
    
    return list(all_threads)





config={"configurable":{"thread_id":"1"}}

# test snippet intentionally removed to avoid import-time execution in Streamlit.



