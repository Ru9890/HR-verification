from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "ResumeVerify AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_verify.db"
    
    # GitHub REST API Token (Optional, boosts rate limit from 60 to 5,000 req/hr)
    GITHUB_TOKEN: Optional[str] = None
    
    # AI / LLM Configurations (Optional)
    LLM_PROVIDER: str = "rule_based" # options: "rule_based", "openai", "gemini", "groq", "ollama"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "llama3:latest"
    
    # Web crawler / request timeouts
    HTTP_TIMEOUT_SECONDS: int = 12
    MAX_REPO_FILE_INSPECTIONS: int = 25
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ResumeVerifyAI/1.0"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
