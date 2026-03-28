import os
from dotenv import load_dotenv

load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

print(tavily_key)
print(anthropic_key)