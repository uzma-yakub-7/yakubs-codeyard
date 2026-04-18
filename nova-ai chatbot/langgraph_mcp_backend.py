# langgraph_mcp_backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool, BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import aiosqlite
import asyncio
import threading
import random

load_dotenv()

# Dedicated async loop for NovaAssist backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()


def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)


def run_async(coro):
    return _submit_async(coro).result()


def submit_async_task(coro):
    """Schedule a coroutine on the NovaAssist backend event loop."""
    return _submit_async(coro)


# -------------------
# 1. LLM
# -------------------
llm = ChatGroq(model="llama-3.1-8b-instant")

# -------------------
# 2. Tools
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
    ideas = [
        f"Start a micro {niche} brand focused on delivery.",
        f"Build a {niche}-focused Instagram page for promotions.",
        f"Offer digital marketing services for local {niche} businesses."
    ]
    return {"niche": niche, "ideas": ideas}


client = MultiServerMCPClient(
    {
        "nova_writing": {
            "transport": "stdio",
            "command": "python3",
            "args": ["/Users/novaassist/Desktop/nova-writing-server/main.py"],
        },
        "nova_content": {
            "transport": "streamable_http",
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)


def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception:
        return []


mcp_tools = load_mcp_tools()

tools = [search_tool, caption_generator, idea_generator, *mcp_tools]
llm_with_tools = llm.bind_tools(tools) if tools else llm

# -------------------
# 3. State
# -------------------
class NovaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
async def nova_node(state: NovaState):
    """NovaAssist writing engine node that may answer or request a tool call."""
    system_message = SystemMessage(content="""
You are NovaAssist, an AI-powered marketing writing engine for businesses.

You have access to these tools:
- caption_generator: Generate social media captions. Call it with topic and category.
- idea_generator: Generate business or content ideas. Call it with a niche.
- duckduckgo_search: Search the web for latest trends and information.

IMPORTANT RULES:
- When user asks for captions, ALWAYS call caption_generator tool immediately.
- When user asks for ideas, ALWAYS call idea_generator tool immediately.
- When user asks for trends or news, ALWAYS call duckduckgo_search.
- For caption_generator, category must be one of: restaurant, coffee, food, fashion, business, salon, gym, bakery, general.
- After getting tool results, present them in a clean friendly format like this:

Here are your captions for [topic]:
1. [caption 1]
2. [caption 2]
3. [caption 3]

- Always be helpful, creative and professional.
""")
    messages = [system_message, *state["messages"]]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools) if tools else None

# -------------------
# 5. Checkpointer
# -------------------
async def _init_checkpointer():
    conn = await aiosqlite.connect(database="nova_memory.db")
    return AsyncSqliteSaver(conn)


checkpointer = run_async(_init_checkpointer())

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(NovaState)
graph.add_node("nova_node", nova_node)
graph.add_edge(START, "nova_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("nova_node", tools_condition)
    graph.add_edge("tools", "nova_node")
else:
    graph.add_edge("nova_node", END)

nova_bot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
async def _alist_sessions():
    all_sessions = set()
    async for checkpoint in checkpointer.alist(None):
        all_sessions.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_sessions)


def retrieve_all_sessions():
    return run_async(_alist_sessions())