from tools.get_weather import get_weather

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

# Registry of all available tools
TOOL_REGISTRY = {
    "get_weather": get_weather,
}

# List of all tool schemas
TOOLS_LIST = [
    WEATHER_TOOL_SCHEMA,
]