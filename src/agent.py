"""Create the grounded Northbridge Hospital policy question-answering agent."""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from src.prompts import SYSTEM_PROMPT
from src.tools import search_kb
from src.settings import get_settings


settings = get_settings()

model = init_chat_model(
    settings.chat_model,
    use_responses_api=True,
    timeout=60,
    max_retries=2,
    api_key=settings.openai_api_key,
)

agent = create_agent(
    model=model,
    tools=[search_kb],
    system_prompt=SYSTEM_PROMPT,
    name="hospital-policy-rag",
)
