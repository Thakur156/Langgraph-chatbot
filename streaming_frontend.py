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

   

    with st.chat_message("assistant"):
        ai_message= st.write_stream(
            message_chunk.content for message_chunk ,metadata in  Chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            )
        )


    st.session_state["message_History"].append({'role':'assistant','content':ai_message})