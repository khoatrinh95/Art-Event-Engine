import os

from dotenv import load_dotenv
from tavily import TavilyClient
import anthropic

def get_clients():
    load_dotenv()
    tavily_key = os.getenv("TAVILY_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not tavily_key:
        print("❌  TAVILY_API_KEY not set. Run: export TAVILY_API_KEY='tvly-...'")
        return None, None
    if not anthropic_key:
        print("❌  ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY='sk-ant-...'")
        return None, None

    tavily_client = TavilyClient(api_key=tavily_key)
    claude_client = anthropic.Anthropic(api_key=anthropic_key)
    return tavily_client, claude_client