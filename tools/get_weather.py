import json
import requests
import os


def get_weather(latitude, longitude):
    """Get the weather condition for a given location using latitude and longitude."""
    if latitude is None:
        return json.dumps({"weatherAPI_response": "Required argument latitude is not provided?"})
    if longitude is None:
        return json.dumps({"weatherAPI_response": "Required argument longitude is not provided?"})
    if latitude > 90 or latitude < -90:
        return json.dumps({"weatherAPI_response": "Invalid latitude value"})
    if longitude > 180 or longitude < -180:
        return json.dumps({"weatherAPI_response": "Invalid longitude value"})

    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    base_url = "https://api.openweathermap.org/data/3.0/onecall?"
    complete_url = f"{base_url}lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    response.raise_for_status()
    weather_data = response.json()

    weather_condition = weather_data["current"]["weather"][0]["description"]
    temperature = weather_data["current"]["temp"]

    return json.dumps({
        "latitude": latitude,
        "longitude": longitude,
        "weather_condition": weather_condition,
        "temperature": temperature
    })