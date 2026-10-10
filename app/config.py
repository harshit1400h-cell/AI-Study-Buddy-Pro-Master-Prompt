import os
import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
CONFIG_FILE = DATA_DIR / "settings.json"

DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

class AppSettings(BaseModel):
    provider: str = "smart_local"  # "smart_local", "gemini", "openai"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    max_chunk_size: int = 800
    chunk_overlap: int = 150
    db_path: str = str(DATA_DIR / "study_buddy.db")

def load_settings() -> AppSettings:
    settings = AppSettings()
    
    # Check env variables first
    env_gemini = os.getenv("GEMINI_API_KEY", "")
    env_openai = os.getenv("OPENAI_API_KEY", "")
    if env_gemini:
        settings.gemini_api_key = env_gemini
        settings.provider = "gemini"
    if env_openai and not env_gemini:
        settings.openai_api_key = env_openai
        settings.provider = "openai"

    # Override with saved user settings if present
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings = AppSettings(**data)
        except Exception:
            pass
            
    return settings

def save_settings(settings: AppSettings):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        # Don't expose keys in log, just save
        f.write(settings.model_dump_json(indent=2))

# Global singleton settings
settings = load_settings()

