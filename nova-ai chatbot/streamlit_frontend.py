# streamlit_frontend.py

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

    response = nova_bot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)

    ai_message = response['messages'][-1].content
    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)