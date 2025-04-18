from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


class Settings(BaseSettings):
    CEREBRAS_API_KEY: str
    SUPABASE_KEY: str
    SUPABASE_URL: str
    TOGETHER_AI: str = Field(..., validation_alias="TOGETHER_AI")
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    DEEPGRAM_API_KEY: str
    CARTESIA_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
