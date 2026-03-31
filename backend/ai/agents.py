from pydantic_ai import Agent
from ai.tools import ALL_TOOLS

repo_agent = Agent("groq:openai/gpt-oss-120b", tools=ALL_TOOLS)
