from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Replace with your WeatherAPI key from https://www.weatherapi.com/my/
WEATHER_API_KEY = 'b58259db815f4b64a7b82300253007'

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    city = 'London'  # Default city
    current_weather = None
    forecast_data = None
    error = None

    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            error = 'Please enter a city name'
        else:
            # Fetch current weather
            current_url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}'
            current_response = requests.get(current_url)
            
            # Fetch forecast (7 days + hourly)
            forecast_url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=7'
            forecast_response = requests.get(forecast_url)

            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_weather = current_response.json()
                forecast_data = forecast_response.json()
            else:
                error = 'Invalid city or API error'

    return render_template('index.html', 
                         city=city, 
                         current_weather=current_weather, 
                         forecast_data=forecast_data, 
                         error=error)

if __name__ == '__main__':
    app.run(debug=True)