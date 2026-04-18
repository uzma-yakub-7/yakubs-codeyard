# streamlit_frontend_threading.py

import streamlit as st
from langgraph_tool_backend import nova_bot, retrieve_all_sessions
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# **************************************** utility functions *************************

def generate_session_id():
    session_id = uuid.uuid4()
    return session_id

def reset_chat():
    session_id = generate_session_id()
    st.session_state['session_id'] = session_id
    add_session(st.session_state['session_id'])
    st.session_state['message_history'] = []

def add_session(session_id):
    if session_id not in st.session_state['chat_sessions']:
        st.session_state['chat_sessions'].append(session_id)

def load_conversation(session_id):
    state = nova_bot.get_state(config={'configurable': {'thread_id': session_id}})
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = generate_session_id()

if 'chat_sessions' not in st.session_state:
    st.session_state['chat_sessions'] = retrieve_all_sessions()

add_session(st.session_state['session_id'])


# **************************************** Sidebar UI *********************************

st.set_page_config(page_title="NovaAssist Writing Engine", page_icon="✍️", layout="centered")

st.sidebar.title('✍️ NovaAssist Writing Engine')
st.sidebar.markdown("Your AI-powered marketing writing assistant.")
st.sidebar.markdown("---")

# Quick guide in sidebar
st.sidebar.markdown("### 💡 What can I help with?")
st.sidebar.markdown("""
- 📸 **Captions** — *Generate captions for my coffee shop*
- 💡 **Ideas** — *Give me business ideas for fashion*
- 💬 **Replies** — *Write a professional reply to a complaint*
""")
st.sidebar.markdown("---")

if st.sidebar.button('➕ New Chat'):
    reset_chat()

st.sidebar.header('🗂️ My Sessions')

for session_id in st.session_state['chat_sessions'][::-1]:
    if st.sidebar.button(str(session_id)):
        st.session_state['session_id'] = session_id
        messages = load_conversation(session_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


# **************************************** Main UI ************************************

st.title("✍️ NovaAssist Writing Engine")
st.caption("Generate captions, business ideas, and professional replies — powered by Groq AI.")

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask NovaAssist — captions, ideas, replies...')

if user_input:

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['session_id']}}

    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in nova_bot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})