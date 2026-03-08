import streamlit as st
from langgraph_database import Chatbot ,retreive_all_threads
from langchain_core.messages import BaseMessage , SystemMessage ,HumanMessage ,AIMessage
import uuid




def generate_thread_id():
    thread_id= str(uuid.uuid4())
    return thread_id


def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_History']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_list']:
        st.session_state['chat_list'].append(thread_id)

def load_conversation(thread_id):
    state = Chatbot.get_state(config={"configurable":{"thread_id":thread_id}})
    if not state or not state.values:
        return []
    return state.values.get('messages', [])



#session state dict -> pressing enter donot erase 

if 'message_History' not in st.session_state:
    st.session_state["message_History"]=[]


if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_list' not in st.session_state:
    st.session_state['chat_list']=retreive_all_threads()


add_thread(st.session_state['thread_id'])



#sidebar ui

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
     reset_chat()
     
st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_list']:
    if st.sidebar.button(thread_id, key=f"thread_btn_{thread_id}"):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id=thread_id)


        temp_messages= []

        for message in messages:
            if isinstance(message,HumanMessage):
                role  ='user'
            elif isinstance(message, AIMessage):
                role ='assistant'
            else:
                continue

            temp_messages.append({'role':role, 'content':message.content}) 


        st.session_state['message_History']=temp_messages
        st.rerun()
        





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
        config={"configurable":{"thread_id":st.session_state['thread_id']},"run_name":'chat_turn'}
        ai_message= st.write_stream(
            message_chunk.content for message_chunk ,metadata in  Chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            )
        )


    st.session_state["message_History"].append({'role':'assistant','content':ai_message})
