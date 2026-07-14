"""
All LLM calls live here: the Groq client, the system prompts, and the two
functions the rest of the app needs - a plain chat reply, and a tool-selection
decision for the download pipeline.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
)
# SYSTEM PROMPTS
CHAT_SYSTEM_PROMPT = (
    "You are a friendly, helpful assistant embedded in a GitHub-downloading tool. "
    "Answer the user's message normally and concisely, like a regular chatbot. "
    "Do not search or download anything - that only happens when the user "
    "explicitly types the /download command."
)

TOOL_SELECTOR_SYSTEM_PROMPT = """You are a strict AI tool selector for a GitHub automation system.

RULES:
- NEVER invent repo names
- ALWAYS use search_github first if unsure
- Only use download_repo if full_name is valid (owner/repo)

Return ONLY in this exact format, nothing else:
tool_name | argument
"""


def chat_reply(user_input: str) -> str:
    """You are an AI chat bot who help user to download anything from github .
    Plain conversational reply - no tools involved. Used for any message
    that does NOT start with /download."""
    messages = [
        SystemMessage(content=CHAT_SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    response = llm.invoke(messages)
    return str(response.content).strip()


def choose_tool(user_input: str, tools) -> str:
    """Ask the LLM which MCP tool to call (and with what argument) for a
    /download request. Returns the raw "tool_name | argument" string."""
    tool_text = "\n".join(f"{t.name} - {t.description}" for t in tools.tools)

    messages = [
        SystemMessage(content=TOOL_SELECTOR_SYSTEM_PROMPT),
        HumanMessage(content=f"Available tools:\n{tool_text}\n\nUser request:\n{user_input}"),
    ]
    response = llm.invoke(messages)
    return str(response.content).strip()
