from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    
    cerebras_api_key : str = Field(..., validation_alias="CEREBRAS_API_KEY")
    cerebras_base_url : str = Field(..., validation_alias="CEREBRAS_BASE_URL")
    supabase_key : str = Field(..., validation_alias="SUPABASE_KEY")
    supabase_url : str = Field(..., validation_alias="SUPABASE_URL")
    together_ai : str = Field(...,validation_alias="TOGETHER_AI_KEY")
    
    class Config:
        env_file = ".env"

