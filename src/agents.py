from dataclasses import dataclass
from typing import List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModelSettings, OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel, Field
import openai
from supabase import create_async_client, AsyncClient

from settings import Settings


settings = Settings()

# Cerebras Model Definition
cerebras_openai_settings = OpenAIModelSettings(
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
)

cerebras_model_name = "llama-3.3-70b"

cerebras_client = openai.AsyncOpenAI(api_key=settings.cerebras_api_key, base_url=settings.cerebras_base_url)

cerebras_model = OpenAIModel(
    model_name=cerebras_model_name,
    provider=OpenAIProvider(openai_client=cerebras_client),
)

class Form(BaseModel):
    caller_name: str = Field(description="The name of the caller making the request if given, else leave it empty")
    request_type: str = Field(description="The type of request being made out of the list: [technical support, billing, new connection]")
    issue_summary: str = Field(description="Detailed description of 50 lines of the issue being reported by the caller")
    customer_sentiment: str = Field(description="The emotion of the customer to be given in one word out of the list: [happy, sad, angry, frustrated]")

@dataclass
class Deps:
    supabase_url: str = settings.supabase_url
    supabase_key: str = settings.supabase_key
    supabase_client: AsyncClient = create_async_client(supabase_url, supabase_key)

with open("prompts/database_agent_prompt.txt", "r") as file:
    database_agent_prompt = file.read()

with open("prompts/report_agent_prompt.txt", "r") as file:
    report_agent_prompt = file.read()

with open("prompts/call_log_agent_prompt.txt", "r") as file:
    call_log_agent_prompt = file.read()

database_agent = Agent(
    model=cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=database_agent_prompt,
    retries=3,
    result_type=Form
)

call_log_agent = Agent(
    model=cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=call_log_agent_prompt,
    retries=3,
)
