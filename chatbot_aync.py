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
import asyncio
from langgraph.graph.message import add_messages
import sqlite3


load_dotenv()



model=ChatGroq(model="qwen/qwen3-32b", reasoning_format="hidden")



# Tools

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
    

tools= [calculator]

llm_with_tools= model.bind_tools(tools)



class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


#fuction for build graph

def build_graph():

    async def chat_node(state:ChatState):

        messages = state["messages"]

        response = await llm_with_tools.ainvoke(messages)

        return {"messages":[response]}
    

    tool_node= ToolNode(tools)

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

    return Chatbot


async def main():

    Chatbot =build_graph()

    result= await Chatbot.ainvoke(
    {'messages':[HumanMessage(content="Find the modulus of 12345 and 23 and give answer like cricket commentator. So give me this sentence but use the numeric numbers.")]},
   
    )


    print(result['messages'][-1].content)


if __name__=='__main__':
    asyncio.run(main())