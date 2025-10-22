from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    """
    Application configuration settings.

    Attributes:
        allowed_origins (List[str]): List of allowed CORS origins.
    """
    allowed_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.oneflow.ai"
    ])

    class Config:
        env_prefix = "ONEFLOW_"
        case_sensitive = False

# Create a singleton settings instance
settings = Settings()
