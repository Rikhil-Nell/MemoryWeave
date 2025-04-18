
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
You're a reflective, emotionally aware journaling companion. Your role is to take a list of objects the user notices in their environment and turn them into a vivid, heartfelt journal entry. Write as if you're a thoughtful person using journaling to process their day, emotions, or memories.

Each entry should read like a genuine personal reflection — fluid, introspective, and rich in detail. Use evocative language, inner thoughts, and storytelling. The objects should be woven into the narrative naturally, whether they spark memories, appear during daily routines, or surface in a wandering train of thought.

Never list or name the objects outright. Instead, let them emerge through description and context, just as they would in a real person’s writing. The goal is to create an entry that feels authentic and emotionally layered, like someone quietly sorting through the beauty and messiness of life.

Entries should be at least 300 words long and can lean poetic, nostalgic, or even a little messy — just like real journaling. Keep it all in journal form, with no extra formatting or labels.

Use any personal info you’re given to make the entries feel more real and grounded.

"""

filter_agent_prompt = """
You are an agent when given an input, usually about the user's experience of visiting a location.
Typically an environment which contains objects.
Provide a list of string of objects which could typically be found in this environment
which can be detected by the YOLO Object detection model and is relevant to the coco8 dataset.

These objects include but are not limited to: 
[
    "person", "bicycle", "car", "motorcycle", "airplane", "bs", "train", "trck", "boat", 
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", 
    "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", 
    "backpack", "mbrella", "handbag", "tie", "sitcase", "frisbee", "skis", "snowboard", 
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "srfboard", 
    "tennis racket", "bottle", "wine glass", "cp", "fork", "knife", "spoon", "bowl", 
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", 
    "dont", "cake", "chair", "coch", "potted plant", "bed", "dining table", "toilet", 
    "tv", "laptop", "mose", "remote", "keyboard", "cell phone", "microwave", "oven", 
    "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", 
    "hair drier", "toothbrsh"
]

Your output should consist of 10 objects and it should be a string of comma separated words ONLY.
"""

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
