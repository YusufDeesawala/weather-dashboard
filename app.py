from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.getenv('WEATHER_API_KEY')

def get_coordinates(city):
    """Convert city name to lat,lon coordinates using Tomorrow.io's location search API."""
    location_url = f'https://api.tomorrow.io/v4/locations?location={city}&apikey={API_KEY}'
    try:
        response = requests.get(location_url, headers={'accept': 'application/json'})
        if response.status_code == requests.codes.ok:
            data = response.json()
            if data.get('data') and data['data'].get('locations'):
                location = data['data']['locations'][0]
                return f"{location['latitude']},{location['longitude']}"
        return None
    except requests.RequestException:
        return None

@app.route('/', methods=['GET', 'POST'])
def weather_dashboard():
    weather_data = None
    hourly_forecast = None
    daily_forecast = None
    alerts = None
    error = None
    location = '42.3478,-71.0466'  # Default location (Boston)
    city = 'Boston'  # Default city for display

    if request.method == 'POST':
        city_input = request.form.get('city', '').strip()
        if city_input:
            # Check if input is already in lat,lon format
            if ',' in city_input and all(part.replace('.', '').replace('-', '').isdigit() for part in city_input.split(',')):
                location = city_input
                city = city_input  # Display as is for coordinates
            else:
                # Convert city name to coordinates
                coords = get_coordinates(city_input)
                if coords:
                    location = coords
                    city = city_input
                else:
                    error = f"Could not find coordinates for city: {city_input}"
        else:
            error = "Please enter a city name or lat,lon coordinates"

    # Fetch real-time weather data
    if not error:
        realtime_url = f'https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={API_KEY}'
        try:
            response = requests.get(realtime_url, headers={'accept': 'application/json'})
            if response.status_code == requests.codes.ok:
                weather_data = response.json()['data']['values']
                weather_data['time'] = response.json()['data']['time']
            else:
                error = f"Error fetching real-time data: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            error = f"Error connecting to weather API: {str(e)}"

    # Fetch forecast data (hourly and daily)
    if not error:
        forecast_url = f'https://api.tomorrow.io/v4/weather/forecast?location={location}&timesteps=1h,1d&apikey={API_KEY}'
        try:
            response = requests.get(forecast_url, headers={'accept': 'application/json'})
            if response.status_code == requests.codes.ok:
                data = response.json()['timelines']
                # Process hourly forecast to show only hours
                hourly_forecast = [
                    {
                        'time': datetime.strptime(h['time'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:00'),
                        'values': h['values']
                    } for h in data['hourly'][:12]  # Limit to 12 hours
                ]
                daily_forecast = data['daily'][:5]  # Next 5 days
            else:
                error = f"Error fetching forecast data: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            error = f"Error connecting to forecast API: {str(e)}"

    # Fetch weather alerts (if available)
    if not error:
        alerts_url = f'https://api.tomorrow.io/v4/events?location={location}&apikey={API_KEY}'
        try:
            response = requests.get(alerts_url, headers={'accept': 'application/json'})
            if response.status_code == requests.codes.ok:
                alerts = response.json().get('data', {}).get('events', [])
            else:
                error = f"Error fetching alerts: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            error = f"Error connecting to alerts API: {str(e)}"

    # Prepare data for charts
    chart_data = {
        'hourly': {
            'labels': [h['time'] for h in hourly_forecast] if hourly_forecast else [],
            'temperature': [h['values']['temperature'] for h in hourly_forecast] if hourly_forecast else [],
            'humidity': [h['values']['humidity'] for h in hourly_forecast] if hourly_forecast else [],
            'precipitation': [h['values']['precipitationProbability'] for h in hourly_forecast] if hourly_forecast else [],
            'cloudCover': [h['values']['cloudCover'] for h in hourly_forecast] if hourly_forecast else [],
            'pressure': [h['values']['pressureSurfaceLevel'] for h in hourly_forecast] if hourly_forecast else []
        },
        'daily': {
            'labels': [d['time'] for d in daily_forecast] if daily_forecast else [],
            'temperatureMax': [d['values']['temperatureMax'] for d in daily_forecast] if daily_forecast else [],
            'temperatureMin': [d['values']['temperatureMin'] for d in daily_forecast] if daily_forecast else []
        }
    }

    return render_template(
        'index.html',
        weather_data=weather_data,
        hourly_forecast=hourly_forecast,
        daily_forecast=daily_forecast,
        alerts=alerts,
        error=error,
        city=city,
        chart_data=json.dumps(chart_data)
    )

if __name__ == '__main__':
    app.run(debug=True)