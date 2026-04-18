# streamlit_frontend_database.py

import streamlit as st
from langgraph_database_backend import nova_bot, retrieve_all_sessions
from langchain_core.messages import HumanMessage
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
                role='user'
            else:
                role='assistant'
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

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["session_id"]},
        "metadata": {
            "thread_id": st.session_state["session_id"]
        },
        "run_name": "nova_chat_turn",
    }

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in nova_bot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})