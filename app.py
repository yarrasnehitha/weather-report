"""Look up current weather for a city using Open-Meteo."""

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers", 85: "Slight snow showers",
    86: "Heavy snow showers", 95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def fetch_json(url, params):
    with urlopen(f"{url}?{urlencode(params)}", timeout=15) as response:
        return json.load(response)


def main():
    city = input("Enter city name: ").strip()
    if not city:
        print("Please enter a city name.")
        return
    try:
        locations = fetch_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": city, "count": 1, "language": "en", "format": "json"},
        ).get("results", [])
        if not locations:
            print("City not found. Check the spelling and try again.")
            return
        location = locations[0]
        data = fetch_json("https://api.open-meteo.com/v1/forecast", {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day",
            "timezone": "auto",
        })
        weather = data["current"]
        place = ", ".join(filter(None, [
            location["name"], location.get("admin1"), location.get("country")
        ]))
        code = weather['weather_code']
        if code in (0, 1):
            description = "It is sunny" if weather['is_day'] else "The sky is clear"
        elif code == 2:
            description = "It is partly cloudy"
        elif code == 3:
            description = "It is cloudy"
        elif code in (45, 48):
            description = "It is foggy"
        elif code in (51, 53, 55):
            description = "It is drizzling"
        elif code in (56, 57):
            description = "There is freezing drizzle"
        elif code in (61, 63, 65, 80, 81, 82):
            description = "It is raining"
        elif code in (66, 67):
            description = "There is freezing rain"
        elif code in (71, 73, 75, 77, 85, 86):
            description = "It is snowing"
        elif code in (95, 96, 99):
            description = "There is a thunderstorm"
        else:
            description = "Weather conditions are unavailable"

        temperature = weather['temperature_2m']
        warmth = "hot" if temperature >= 30 else "warm" if temperature >= 20 else "cool" if temperature >= 10 else "cold"
        print(f"\nTemperature: {temperature} C")
        print(f"Description: {description}.")
        print(f"\n{place} is currently experiencing {warmth} weather.")
        print(f"Conditions: {DESCRIPTIONS.get(code, 'Unknown conditions').lower()}.")
        print(f"It feels like {weather['apparent_temperature']} C, with humidity at {weather['relative_humidity_2m']}%.")
        print(f"Winds are blowing at {weather['wind_speed_10m']} km/h.")
    except (URLError, TimeoutError, OSError):
        print("Unable to fetch weather. Check your internet connection and try again.")
    except (ValueError, KeyError, TypeError):
        print("The weather service returned unexpected data. Please try again later.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nWeather lookup cancelled.")
