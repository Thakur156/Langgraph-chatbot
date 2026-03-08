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
from langchain_mcp_adapters import MultiServerMCPClient


load_dotenv()



model=ChatGroq(model="qwen/qwen3-32b", reasoning_format="hidden")


client = MultiServerMCPClient(
    {
       
         "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
        
    }
)




class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


#fuction for build graph

async def build_graph():
    

    tools= await client.get_tools()
    llm_with_tools= model.bind_tools(tools)

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

    Chatbot = await build_graph()

    result= await Chatbot.ainvoke(
    {'messages':[HumanMessage(content="add an expense rs 500 on udemy course on 10nov")]},
   
    )


    print(result['messages'][-1].content)


if __name__=='__main__':
    asyncio.run(main())