from flask import Flask, render_template, request
import requests
from datetime import datetime
import json

app = Flask(__name__)

# Replace with your actual WeatherAPI key
API_KEY = "b58259db815f4b64a7b82300253007"  # Replace with your WeatherAPI key
BASE_URL = "http://api.weatherapi.com/v1"

# Map WeatherAPI condition codes to custom SVG icons and background styles
WEATHER_STYLES = {
    1000: {"icon": "/static/icons/sunny.svg", "background": "radial-gradient(circle at 50% 50%, #FFD700 0%, #FFA500 50%, #87CEEB 100%)"},  # Sunny
    1003: {"icon": "/static/icons/partly-cloudy.svg", "background": "radial-gradient(circle at 50% 50%, #B0C4DE 0%, #87CEEB 50%, #4682B4 100%)"},  # Partly cloudy
    1006: {"icon": "/static/icons/cloudy.svg", "background": "radial-gradient(circle at 50% 50%, #A9A9A9 0%, #778899 50%, #2F4F4F 100%)"},  # Cloudy
    1009: {"icon": "/static/icons/overcast.svg", "background": "radial-gradient(circle at 50% 50%, #808080 0%, #696969 50%, #2F4F4F 100%)"},  # Overcast
    1063: {"icon": "/static/icons/rain.svg", "background": "radial-gradient(circle at 50% 50%, #4682B4 0%, #1E90FF 50%, #000080 100%)"},  # Patchy rain
    1183: {"icon": "/static/icons/rain.svg", "background": "radial-gradient(circle at 50% 50%, #4682B4 0%, #1E90FF 50%, #000080 100%)"},  # Moderate rain
    1213: {"icon": "/static/icons/snow.svg", "background": "radial-gradient(circle at 50% 50%, #F0F8FF 0%, #E6E6FA 50%, #B0C4DE 100%)"},  # Snow
    # Add more mappings as needed
}

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    location = "London"
    forecast_days = 5
    error = None
    unit = "C"  # Default to Celsius

    if request.method == "POST":
        location = request.form.get("location", "London").strip()
        forecast_days = int(request.form.get("forecast_days", 5))
        unit = request.form.get("unit", "C")
        if forecast_days not in [5, 10, 30]:
            forecast_days = 5

        # Handle coordinates from geolocation
        if "," in location:
            try:
                lat, lon = map(float, location.split(","))
                location = f"{lat},{lon}"
            except ValueError:
                error = "Invalid coordinates format"
                location = "London"

        # Fetch current weather
        current_url = f"{BASE_URL}/current.json?key={API_KEY}&q={location}&aqi=yes"
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            weather_data = response.json()
        except requests.exceptions.RequestException as e:
            error = f"Error fetching current weather: {str(e)}"
            weather_data = None

        # Fetch forecast
        forecast_url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={location}&days={forecast_days}&aqi=no&alerts=yes"
        try:
            response = requests.get(forecast_url)
            response.raise_for_status()
            forecast_data = response.json()
        except requests.exceptions.RequestException as e:
            error = f"Error fetching forecast: {str(e)}" if not error else error
            forecast_data = None

    # Prepare style for current weather
    current_style = WEATHER_STYLES.get(weather_data["current"]["condition"]["code"], WEATHER_STYLES[1000]) if weather_data else WEATHER_STYLES[1000]

    return render_template(
        "index.html",
        weather_data=weather_data,
        forecast_data=forecast_data,
        location=location,
        forecast_days=forecast_days,
        error=error,
        unit=unit,
        weather_styles=WEATHER_STYLES,
        current_style=current_style
    )

if __name__ == "__main__":
    app.run(debug=True)