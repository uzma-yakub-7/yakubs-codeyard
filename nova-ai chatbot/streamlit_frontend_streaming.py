# streamlit_frontend_streaming.py

import streamlit as st
from langgraph_backend import nova_bot
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="NovaAssist Writing Engine", page_icon="✍️", layout="centered")

# st.session_state -> dict ->
CONFIG = {'configurable': {'thread_id': 'nova-session-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

st.title("✍️ NovaAssist Writing Engine")
st.caption("Your AI-powered marketing writing assistant — captions, ideas, and replies.")

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask NovaAssist — captions, ideas, replies...')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in nova_bot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= {'configurable': {'thread_id': 'nova-session-1'}},
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})