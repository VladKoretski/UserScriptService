import os
from dotenv import load_dotenv

load_dotenv()

def get_config() -> dict:
    return {
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_URL": os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        "LLM_TEMPERATURE": float(os.getenv("LLM_TEMPERATURE", "0.3")),
        "CACHE_TTL": int(os.getenv("CACHE_TTL", "600")),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }