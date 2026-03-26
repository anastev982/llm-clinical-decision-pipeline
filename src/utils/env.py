from pathlib import Path
import os
from dotenv import load_dotenv

def load_env() -> None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
            return
    raise FileNotFoundError("No .env file found in parent directories.")