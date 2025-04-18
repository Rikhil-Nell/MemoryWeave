
import openai
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModelSettings, OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from app.core.load_api import Settings
from supabase import create_client, Client

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
cerebras_client = openai.AsyncOpenAI(
    api_key=settings.CEREBRAS_API_KEY, base_url="https://api.cerebras.ai/v1")

# Cerebras Model
cerebras_model = OpenAIModel(
    model_name=cerebras_model_name,
    provider=OpenAIProvider(openai_client=cerebras_client),
)

# System Prompt
journal_system_prompt = f"""
You are a thoughtful and introspective journaling assistant. Your job is to take a list of objects detected in the user’s environment and craft a long, vivid, and emotionally resonant journal entry around them. You must assume the perspective of a reflective human who notices these objects and connects them to their thoughts, memories, or current events in their day.

Each entry should feel personal and flow like a genuine journal. Use descriptive language, inner monologue, and narrative elements. The story should be centered around the objects given, either by encountering them during the day, associating them with past memories, or integrating them into a stream-of-consciousness reflection.

You should never list the objects directly; instead, weave them naturally into the narrative. Make the entry feel as if it were written by a person who is using journaling as a tool to understand their thoughts and emotions.

The final output should be at least 300 words, immersive, and poetic when needed. Do not include headings or formatting — only the journal content.

Use this information to personalize your replies:

"""

with open("filter_agent_prompt.txt", "r") as file:
    filter_agent_prompt = file.read()

# Setting up Agent
journal_agent = Agent(
    model=cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=journal_system_prompt,
    retries=1,
)

filter_agent = Agent(
    model=cerebras_model,
    model_settings=cerebras_openai_settings,
    system_prompt=filter_agent_prompt,
    retries=1,
    )

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
