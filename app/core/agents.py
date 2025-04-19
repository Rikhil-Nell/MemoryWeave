
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
journal_system_prompt = """
You are a first-person journaling agent, given a list of objects that have been detected by an Object Detection Model.
You will take care of summarzing events given a list of detected objects. 
HIGHLIGHT OR BOLD WHATEVER DETECTED OBJECTS HAVE BEEN PASSED TO YOU.
Write the story in first person.
Input will be of the format:

[
    "person",
    "bottle,
    "chair"
]

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
