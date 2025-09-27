import os
from dotenv import load_dotenv

load_dotenv("azureopenai.env")

class Config:
    """Configuration for the vision bot"""

    # Azure OpenAI settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = "2024-05-01-preview"
    AZURE_OPENAI_MODEL = 'gpt-4.1-mini'

    # Weather API Settings
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    # Assistant Settings
    ASSISTANT_NAME = "Vision Assistant"
    ASSISTANT_INSTRUCTIONS = (
        "You are a vision assistant that assists the user with computer visionn related tasks"
    )

    # conversation settings
    POLL_INTERVAL_SEC = 1.5
    MAX_WAIT_SEC = 90