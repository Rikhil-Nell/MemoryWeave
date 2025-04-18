from dataclasses import dataclass
from typing import List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModelSettings, OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel, Field
import openai
import questionary
from supabase import create_async_client, AsyncClient
import asyncio
from load_api import Settings
from questionary import text


settings = Settings()

# Cerebras Model Definition
cerebras_openai_settings = OpenAIModelSettings(
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
)

cerebras_model_name = "llama-3.3-70b"

cerebras_client = openai.AsyncOpenAI(api_key=settings.CEREBRAS_API_KEY, base_url="https://api.cerebras.ai/v1")

cerebras_model = OpenAIModel(
    model_name=cerebras_model_name,
    provider=OpenAIProvider(openai_client=cerebras_client),
)


class Memory(BaseModel):
    date: str
    objects_seen: List[str]
    summary: str

class MemoryContext(BaseModel):
    memories: List[Memory]


memories = [
    Memory(date="2025-04-01", objects_seen=["cat", "sofa", "sunlight"], summary="A cozy afternoon with a cat lounging."),
    Memory(date="2025-04-10", objects_seen=["books", "coffee"], summary="Reading session in the morning."),
]

memories_text = "\n".join(
    f"On {m.date}, you saw {', '.join(m.objects_seen)}. Summary: {m.summary}" for m in memories
)

system_prompt = f"""
You need to create a journal like story for each object detected at an event. Here's what the user has experienced recently:
{memories_text}

Use this information to personalize your replies.
"""

# Now pass system_prompt to your agent setup

agent = Agent(
    model = cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=system_prompt,
    retries=2,
)


user_input = 'Provide the journal'
response = asyncio.run(agent.run(user_input))
print(response.data)





# class Return(BaseModel):
#     pass

# @dataclass
# class Deps:
#     supabase_url: str = settings.supabase_url
#     supabase_key: str = settings.supabase_key
#     supabase_client: AsyncClient = create_async_client(supabase_url, supabase_key)

# with open("prompts/database_agent_prompt.txt", "r") as file:
#     database_agent_prompt = file.read()

# with open("prompts/report_agent_prompt.txt", "r") as file:
#     report_agent_prompt = file.read()

# with open("prompts/call_log_agent_prompt.txt", "r") as file:
#     call_log_agent_prompt = file.read()

# database_agent = Agent(
#     model=cerebras_model,
#     model_settings=cerebras_openai_settings,
#     system_prompt=database_agent_prompt,
#     retries=3,
#     result_type=Return
# )

# call_log_agent = Agent(
#     model=cerebras_model,
#     model_settings=cerebras_openai_settings,
#     system_prompt=call_log_agent_prompt,
#     retries=3,
# )
