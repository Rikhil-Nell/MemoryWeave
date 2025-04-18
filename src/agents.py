
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModelSettings, OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
import openai
import asyncio
from load_api import Settings

# from supabase import create_async_client, AsyncClient
# from dataclasses import dataclass

settings = Settings()

# Cerebras Model Definition
cerebras_openai_settings = OpenAIModelSettings(
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
)

# Model Name
cerebras_model_name = "llama-3.3-70b"

# Setting Client Up
cerebras_client = openai.AsyncOpenAI(api_key=settings.CEREBRAS_API_KEY, base_url="https://api.cerebras.ai/v1")


# Cerebras Model
cerebras_model = OpenAIModel(
    model_name=cerebras_model_name,
    provider=OpenAIProvider(openai_client=cerebras_client),
)


# Validation Models
class Memory(BaseModel):
    date: str
    objects_seen: List[str]
    summary: str

class MemoryContext(BaseModel):
    memories: List[Memory]


# Needs to be updated through YOLO IMG Detection
memories = [
    Memory(date="2025-04-01", objects_seen=["cat", "sofa", "sunlight"], summary="A cozy afternoon with a cat lounging."),
    Memory(date="2025-04-10", objects_seen=["books", "coffee"], summary="Reading session in the morning."),
]


# Converting to a string
memories_text = "\n".join(
    f"On {m.date}, you saw {', '.join(m.objects_seen)}. Summary: {m.summary}" for m in memories
)


# System Prompt
system_prompt = f"""
You need to create a journal like story for each object detected at an event. Here's what the user has experienced recently:
{memories_text}

Use this information to personalize your replies.
"""

# Setting up Agent
agent = Agent(
    model = cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=system_prompt,
    retries=2,
)

# Testing the Agent's Function
user_input = 'Provide the journal'
response = asyncio.run(agent.run(user_input))
print(response.data)


class Return(BaseModel):
    pass


# Dataclass for DB AGENT
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
