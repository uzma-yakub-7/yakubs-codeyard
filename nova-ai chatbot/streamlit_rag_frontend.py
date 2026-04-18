# streamlit_rag_frontend.py (future advancements)

import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langraph_rag_backend import (
    nova_bot,
    ingest_pdf,
    retrieve_all_sessions,
    session_document_metadata,
)

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

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_session(st.session_state["session_id"])

session_key = str(st.session_state["session_id"])
session_docs = st.session_state["ingested_docs"].setdefault(session_key, {})
sessions = st.session_state["chat_sessions"][::-1]
selected_session = None

# ============================ Sidebar ============================
st.sidebar.title("✍️ NovaAssist Writing Engine")
st.sidebar.markdown(f"**Session ID:** `{session_key}`")
st.sidebar.markdown("---")

st.sidebar.markdown("### 💡 What can I help with?")
st.sidebar.markdown("""
- 📸 **Captions** — *Generate captions for my coffee shop*
- 💡 **Ideas** — *Give me business ideas for fashion*
- 🔍 **Search** — *Search latest marketing trends*
- 💬 **Replies** — *Write a professional reply to a complaint*
- 📄 **PDF** — *Upload a PDF and ask questions about it*
""")
st.sidebar.markdown("---")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

if session_docs:
    latest_doc = list(session_docs.values())[-1]
    st.sidebar.success(
        f"Using `{latest_doc.get('filename')}` "
        f"({latest_doc.get('chunks')} chunks from {latest_doc.get('documents')} pages)"
    )
else:
    st.sidebar.info("No PDF indexed yet. Upload one to get started!")

uploaded_pdf = st.sidebar.file_uploader("📄 Upload a PDF for this session", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name in session_docs:
        st.sidebar.info(f"`{uploaded_pdf.name}` already processed for this session.")
    else:
        with st.sidebar.status("Indexing PDF…", expanded=True) as status_box:
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                session_id=session_key,
                filename=uploaded_pdf.name,
            )
            session_docs[uploaded_pdf.name] = summary
            status_box.update(label="✅ PDF indexed successfully!", state="complete", expanded=False)

st.sidebar.subheader("🗂️ Past Sessions")
if not sessions:
    st.sidebar.write("No past sessions yet.")
else:
    for session_id in sessions:
        if st.sidebar.button(str(session_id), key=f"side-session-{session_id}"):
            selected_session = session_id

# ============================ Main Layout ========================
st.title("✍️ NovaAssist Writing Engine")
st.caption("Generate captions, business ideas, professional replies, and chat with your PDFs — powered by Groq AI.")

# Chat area
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Ask NovaAssist — captions, ideas, replies, or about your PDF...")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": session_key},
        "metadata": {"thread_id": session_key},
        "run_name": "nova_chat_turn",
    }

    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, _ in nova_bot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
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

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ NovaAssist done!", state="complete", expanded=False
            )

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    doc_meta = session_document_metadata(session_key)
    if doc_meta:
        st.caption(
            f"Document indexed: {doc_meta.get('filename')} "
            f"(chunks: {doc_meta.get('chunks')}, pages: {doc_meta.get('documents')})"
        )

st.divider()

if selected_session:
    st.session_state["session_id"] = selected_session
    messages = load_conversation(selected_session)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})
    st.session_state["message_history"] = temp_messages
    st.session_state["ingested_docs"].setdefault(str(selected_session), {})
    st.rerun()