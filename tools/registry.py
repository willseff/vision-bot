from tools.get_weather import get_weather
from tools.smart_crop import smart_crop_image, crop_image
from tools.upscale import upscale_image

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

UPSCALE_IMAGE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "upscale_image",
        "description": (
            "Upscale the uploaded image using OpenCV EDSR model deployed on Azure Container Apps. "
            "This function enhances image resolution using deep learning super-resolution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "scale": {
                    "type": "integer", 
                    "description": "Upscaling factor (2, 3, or 4). Default is 2.",
                    "enum": [2, 3, 4]
                },
            },
            "required": [],
        },
    },
}



# Registry of all available tools
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "smart_crop_image": smart_crop_image,
    "crop_image": crop_image,
    "upscale_image": upscale_image,
}

# List of all tool schemas
TOOLS_LIST = [
    WEATHER_TOOL_SCHEMA,
    SMART_CROP_TOOL_SCHEMA,
    CROP_IMAGE_TOOL_SCHEMA,
    UPSCALE_IMAGE_TOOL_SCHEMA,
]