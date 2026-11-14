
import app as weather_backend

from flask import Flask, request, jsonify, render_template
from urllib.error import URLError

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return render_template("index.html")


@web_app.route("/weather")
def get_weather():

    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    try:
        locations = weather_backend.fetch_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }
        ).get("results", [])

        if not locations:
            return jsonify({"error": "City not found."}), 404

        location = locations[0]

        data = weather_backend.fetch_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,apparent_temperature,"
                    "relative_humidity_2m,weather_code,"
                    "wind_speed_10m,is_day"
                ),
                "timezone": "auto"
            }
        )

        weather = data["current"]
        code = weather["weather_code"]

        place = ", ".join(filter(None, [
            location["name"],
            location.get("admin1"),
            location.get("country")
        ]))

        if code in (0, 1):
            description = (
                "It is sunny" if weather["is_day"]
                else "The sky is clear"
            )
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

        temperature = weather["temperature_2m"]

        warmth = (
            "hot" if temperature >= 30
            else "warm" if temperature >= 20
            else "cool" if temperature >= 10
            else "cold"
        )

        return jsonify({
            "city": place,
            "temperature": temperature,
            "description": description,
            "conditions": weather_backend.DESCRIPTIONS.get(
                code, "Unknown conditions"
            ),
            "feels_like": weather["apparent_temperature"],
            "humidity": weather["relative_humidity_2m"],
            "wind_speed": weather["wind_speed_10m"],
            "summary": (
                f"{place} is currently experiencing {warmth} weather. "
                f"Conditions: "
                f"{weather_backend.DESCRIPTIONS.get(code, 'Unknown conditions').lower()}. "
                f"It feels like {weather['apparent_temperature']} C, "
                f"with humidity at {weather['relative_humidity_2m']}%. "
                f"Winds are blowing at {weather['wind_speed_10m']} km/h."
            )
        })

    except (URLError, TimeoutError, OSError):
        return jsonify({
            "error": "Unable to fetch weather. Check your internet connection."
        }), 503

    except (ValueError, KeyError, TypeError):
        return jsonify({
            "error": "Unexpected weather data. Please try again later."
        }), 502


if __name__ == "__main__":
    web_app.run(debug=True)
