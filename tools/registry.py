from tools.get_weather import get_weather
from tools.smart_crop import smart_crop_image, crop_image

# Define the tool schema for the Assistant API
WEATHER_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the weather condition using latitude and longitude. "
            "If any argument is missing in the user message, assume it as 'null' and not zero (0) or don't return missing argument value yourself"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the location"},
                "longitude": {"type": "number", "description": "Longitude of the location"},
            },
            "required": ["latitude", "longitude"],
        },
    },
}

SMART_CROP_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "smart_crop_image",
        "description": (
            "Analyze the uploaded image and return smart crop suggestions for different aspect ratios. "
            "This function analyzes the most recently uploaded image and returns optimal crop areas."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "aspect_ratios": {
                    "type": "array", 
                    "items": {"type": "number"}, 
                    "description": "List of aspect ratios for smart cropping (optional, defaults to [0.9, 1.33])"
                },
            },
            "required": [],
        },
    },
}

CROP_IMAGE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "crop_image",
        "description": (
            "Crop the uploaded image using specified bounding box coordinates. "
            "Returns the cropped image as base64 data along with metadata."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate of the top-left corner"},
                "y": {"type": "integer", "description": "Y coordinate of the top-left corner"},
                "width": {"type": "integer", "description": "Width of the crop area"},
                "height": {"type": "integer", "description": "Height of the crop area"},
            },
            "required": ["x", "y", "width", "height"],
        },
    },
}

# Registry of all available tools
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "smart_crop_image": smart_crop_image,
    "crop_image": crop_image,
}

# List of all tool schemas
TOOLS_LIST = [
    WEATHER_TOOL_SCHEMA,
    SMART_CROP_TOOL_SCHEMA,
    CROP_IMAGE_TOOL_SCHEMA,
]