# langgraph_database_backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# NovaAssist Writing Engine - Database Brain
llm = ChatGroq(model="llama-3.1-8b-instant")

class NovaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def nova_node(state: NovaState):
    system_message = SystemMessage(content="""
You are NovaAssist, an AI-powered marketing writing engine for businesses.
Help users generate social media captions, business ideas, and professional replies.
Always be helpful, creative and professional.
""")
    messages = [system_message, *state["messages"]]
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='nova_memory.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(NovaState)
graph.add_node("nova_node", nova_node)
graph.add_edge(START, "nova_node")
graph.add_edge("nova_node", END)

nova_bot = graph.compile(checkpointer=checkpointer)

def retrieve_all_sessions():
    all_sessions = set()
    for checkpoint in checkpointer.list(None):
        all_sessions.add(checkpoint.config['configurable']['thread_id'])

    return list(all_sessions)