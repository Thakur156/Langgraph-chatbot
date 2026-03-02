import streamlit as st
from langgraph_backend import Chatbot
from langchain_core.messages import BaseMessage , SystemMessage ,HumanMessage

#session state dict -> pressing enter donot erase 

if 'message_History' not in st.session_state:
    st.session_state["message_History"]=[]



config={"configurable":{"thread_id":"1"}}





for message in st.session_state["message_History"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input=st.chat_input("Type Here")

if user_input:

    #first add history to messages

    st.session_state["message_History"].append({'role':'user','content':user_input})

    with st.chat_message("user"):
        st.text(user_input)
    
    #first add history to messages


    response= Chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=config)
    ai_message= response['messages'][-1].content

    st.session_state["message_History"].append({'role':'assistant','content':ai_message})

    with st.chat_message("assistant"):
        st.text(ai_message)