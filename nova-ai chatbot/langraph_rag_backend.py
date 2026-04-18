# langraph_rag_backend.py

from __future__ import annotations

import os
import sqlite3
import tempfile
from typing import Annotated, Any, Dict, Optional, TypedDict

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_community.embeddings import FakeEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import random
import requests

load_dotenv()

# -------------------
# 1. LLM
# -------------------
llm = ChatGroq(model="llama-3.1-8b-instant")
embeddings = FakeEmbeddings(size=1536)

# -------------------
# 2. NovaAssist document store (per session)
# -------------------
_SESSION_RETRIEVERS: Dict[str, Any] = {}
_SESSION_METADATA: Dict[str, dict] = {}


def _get_retriever(session_id: Optional[str]):
    """Fetch the retriever for a session if available."""
    if session_id and session_id in _SESSION_RETRIEVERS:
        return _SESSION_RETRIEVERS[session_id]
    return None


def ingest_pdf(file_bytes: bytes, session_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the session.
    Returns a summary dict that can be surfaced in the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _SESSION_RETRIEVERS[str(session_id)] = retriever
        _SESSION_METADATA[str(session_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


# -------------------
# 3. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def caption_generator(topic: str, category: str) -> dict:
    """
    Generate creative social media captions for a given topic and category.
    Supported categories: restaurant, coffee, food, fashion, business, salon, gym, bakery, general
    """
    caption_bank = {
        "restaurant": [
            "Where every bite tells a story. Come taste ours.",
            "Good food. Great vibes. Unforgettable moments.",
            "From our kitchen to your heart — made with love.",
            "Flavors that linger long after the last bite.",
            "Dine with us and let the food do the talking."
        ],
        "coffee": [
            "Your daily dose of warmth, one cup at a time.",
            "Life happens. Coffee helps.",
            "Brewed to perfection. Sipped with love.",
            "Start your day the right way — with us.",
            "Coffee is always a good idea."
        ],
        "food": [
            "Good food is good mood.",
            "Taste the passion in every bite.",
            "Food made with heart, served with soul.",
            "Eat well, live well, feel well.",
            "Because great food brings people together."
        ],
        "fashion": [
            "Wear your confidence. Own your style.",
            "Fashion is what you buy. Style is what you do with it.",
            "Dress like you mean it.",
            "Your outfit is your first impression — make it count.",
            "Style that speaks before you even say a word."
        ],
        "business": [
            "Building brands that people remember.",
            "Your vision. Our strategy. Real results.",
            "Success starts with the right move.",
            "We don't just grow businesses. We build legacies.",
            "Smart ideas. Stronger brands."
        ],
        "salon": [
            "Where beauty meets confidence.",
            "Glow up. Show up. Own it.",
            "Your best look is just an appointment away.",
            "We don't do ordinary. Only extraordinary.",
            "Because you deserve to feel beautiful every day."
        ],
        "gym": [
            "Train hard. Stay humble. Repeat.",
            "Your only competition is yesterday's you.",
            "Sweat today. Shine tomorrow.",
            "Strong body. Stronger mind.",
            "Push your limits. Find your greatness."
        ],
        "bakery": [
            "Baked with love. Served with joy.",
            "Life is short. Eat the cake.",
            "Fresh from the oven. Straight to your heart.",
            "Every bite is a little moment of happiness.",
            "Sweet things are always worth it."
        ],
        "general": [
            "Making moments worth remembering.",
            "Small things done with great love make a big difference.",
            "Every day is a new opportunity. Make it count.",
            "Created with passion. Shared with purpose.",
            "Because some things are just worth celebrating."
        ]
    }

    captions = caption_bank.get(category.lower(), caption_bank["general"])
    selected = random.sample(captions, min(3, len(captions)))
    return {"topic": topic, "category": category, "captions": selected}


@tool
def idea_generator(niche: str) -> dict:
    """
    Generate creative business or content ideas for a given niche or industry.
    Supported niches: food, fashion, tech, cafe, salon, gym, bakery, general
    """
    try:
        ideas = [
            f"Start a micro {niche} brand focused on delivery.",
            f"Build a {niche}-focused Instagram page for promotions.",
            f"Offer digital marketing services for local {niche} businesses."
        ]
        return {"niche": niche, "ideas": ideas}
    except Exception as e:
        return {"error": str(e)}


@tool
def nova_rag_tool(query: str, session_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this NovaAssist session.
    Always include the session_id when calling this tool.
    """
    retriever = _get_retriever(session_id)
    if retriever is None:
        return {
            "error": "No document indexed for this session. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _SESSION_METADATA.get(str(session_id), {}).get("filename"),
    }


tools = [search_tool, caption_generator, idea_generator, nova_rag_tool]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 4. State
# -------------------
class NovaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# -------------------
# 5. Nodes
# -------------------
def nova_node(state: NovaState, config=None):
    """NovaAssist writing engine node that may answer or request a tool call."""
    session_id = None
    if config and isinstance(config, dict):
        session_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
            "You are NovaAssist, an AI-powered marketing writing engine. "
            "You help businesses generate social media captions, business ideas, "
            "and professional replies. For questions about the uploaded PDF, call "
            "the `nova_rag_tool` and include the session_id "
            f"`{session_id}`. You can help with captions,ideas and replies. "
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# -------------------
# 6. Checkpointer
# -------------------
conn = sqlite3.connect(database="nova_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 7. Graph
# -------------------
graph = StateGraph(NovaState)
graph.add_node("nova_node", nova_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "nova_node")
graph.add_conditional_edges("nova_node", tools_condition)
graph.add_edge("tools", "nova_node")

nova_bot = graph.compile(checkpointer=checkpointer)

# -------------------
# 8. Helpers
# -------------------
def retrieve_all_sessions():
    all_sessions = set()
    for checkpoint in checkpointer.list(None):
        all_sessions.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_sessions)


def session_has_document(session_id: str) -> bool:
    return str(session_id) in _SESSION_RETRIEVERS


def session_document_metadata(session_id: str) -> dict:
    return _SESSION_METADATA.get(str(session_id), {})