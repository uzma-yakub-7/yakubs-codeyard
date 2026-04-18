# streamlit_frontend_mcp.py

import queue
import uuid

import streamlit as st
from langgraph_mcp_backend import nova_bot, retrieve_all_sessions, submit_async_task
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

st.set_page_config(page_title="NovaAssist Writing Engine", page_icon="✍️", layout="centered")

# =========================== Utilities ===========================
def generate_session_id():
    return uuid.uuid4()


def reset_chat():
    session_id = generate_session_id()
    st.session_state["session_id"] = session_id
    add_session(session_id)
    st.session_state["message_history"] = []


def add_session(session_id):
    if session_id not in st.session_state["chat_sessions"]:
        st.session_state["chat_sessions"].append(session_id)


def load_conversation(session_id):
    state = nova_bot.get_state(config={"configurable": {"thread_id": session_id}})
    return state.values.get("messages", [])


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = generate_session_id()

if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = retrieve_all_sessions()

add_session(st.session_state["session_id"])

# ============================ Sidebar ============================
st.sidebar.title("✍️ NovaAssist Writing Engine")
st.sidebar.markdown("Your AI-powered marketing writing assistant.")
st.sidebar.markdown("---")

st.sidebar.markdown("### 💡 What can I help with?")
st.sidebar.markdown("""
- 📸 **Captions** — *Generate captions for my coffee shop*
- 💡 **Ideas** — *Give me business ideas for fashion*
- 💬 **Replies** — *Write a professional reply to a complaint*
""")
st.sidebar.markdown("---")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.header("🗂️ My Sessions")
for session_id in st.session_state["chat_sessions"][::-1]:
    if st.sidebar.button(str(session_id)):
        st.session_state["session_id"] = session_id
        messages = load_conversation(session_id)

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages

# ============================ Main UI ============================

st.title("✍️ NovaAssist Writing Engine")
st.caption("Generate captions, business ideas, and professional replies — powered by Groq AI.")

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Ask NovaAssist — captions, ideas, replies...")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["session_id"]},
        "metadata": {"thread_id": st.session_state["session_id"]},
        "run_name": "nova_chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            event_queue: queue.Queue = queue.Queue()

            async def run_stream():
                try:
                    async for message_chunk, metadata in nova_bot.astream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages",
                    ):
                        event_queue.put((message_chunk, metadata))
                except Exception as exc:
                    event_queue.put(("error", exc))
                finally:
                    event_queue.put(None)

            submit_async_task(run_stream())

            while True:
                item = event_queue.get()
                if item is None:
                    break
                message_chunk, metadata = item
                if message_chunk == "error":
                    raise metadata

                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"✍️ NovaAssist using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"✍️ NovaAssist using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ NovaAssist done!", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )