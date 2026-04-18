# langgraph_tool_backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import random

load_dotenv()

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

    return {
        "topic": topic,
        "category": category,
        "captions": selected
    }


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


tools = [search_tool, caption_generator, idea_generator]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class NovaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def nova_node(state: NovaState):
    """NovaAssist writing engine node that may answer or request a tool call."""

    system_message = SystemMessage(content="""
You are NovaAssist, an AI-powered marketing writing engine for businesses.

You have access to these tools:
- caption_generator: Use this to generate social media captions. Call it with topic and category.
- idea_generator: Use this to generate business or content ideas. Call it with a niche.
- duckduckgo_search: Use this to search the web for latest trends and information.

IMPORTANT RULES:
- When user asks for captions, ALWAYS call caption_generator tool immediately.
- When user asks for ideas, ALWAYS call idea_generator tool immediately.
- When user asks for trends or news, ALWAYS call duckduckgo_search.
- For caption_generator, category must be one of: restaurant, coffee, food, fashion, business, salon, gym, bakery, general.
- For idea_generator, niche can be any business type.
- After getting tool results, present them in a clean friendly format like this:

Here are your captions for [topic]:
1. [caption 1]
2. [caption 2]
3. [caption 3]

- Always be helpful, creative and professional.

Example interactions:
- User: "Generate captions for my restaurant" → call caption_generator(topic="restaurant", category="restaurant")
- User: "Give me ideas for a fashion business" → call idea_generator(niche="fashion")
- User: "Generate captions for my coffee shop" → call caption_generator(topic="coffee shop", category="coffee")
- User: "Write captions for my gym" → call caption_generator(topic="gym", category="gym")
- User: "Give me salon business ideas" → call idea_generator(niche="salon")
- User: "Search latest social media trends" → call duckduckgo_search(query="latest social media marketing trends 2026")
""")

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database="nova_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(NovaState)
graph.add_node("nova_node", nova_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "nova_node")

graph.add_conditional_edges("nova_node", tools_condition)
graph.add_edge('tools', 'nova_node')

nova_bot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_sessions():
    all_sessions = set()
    for checkpoint in checkpointer.list(None):
        all_sessions.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_sessions)