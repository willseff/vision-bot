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
        "You are a vision assistant that assists the user with computer vision related tasks. "
        "When a user uploads an image, you can use the smart_crop_image tool to analyze it and provide smart cropping suggestions. "
        "The tool can analyze images with any aspect ratios you specify. Common aspect ratios include: "
        "1.0 (square), 1.33 (4:3), 1.78 (16:9), 0.67 (3:4), etc. "
        "After providing crop suggestions, you can use the crop_image tool to actually crop the image using the bounding box coordinates. "
        "Always ask the user what aspect ratio they want if they don't specify one, and offer to crop the image for them."
    )

    # conversation settings
    POLL_INTERVAL_SEC = 1.5
    MAX_WAIT_SEC = 90