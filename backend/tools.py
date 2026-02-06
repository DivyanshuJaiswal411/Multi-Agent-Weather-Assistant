import os
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = "YOUR_KEY"

if not OPENWEATHER_API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY is not set")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_weather(city: str):
    """
    Get the current weather for a given city.
    
    Args:
        city: The name of the city (e.g., "London", "New York").
    """
    logger.info(f"Fetching current weather for {city}")
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        
        return (
            f"Current Weather in {city}: {desc.capitalize()}\n"
            f"Temperature: {temp}°C (Feels like {feels_like}°C).\n"
            f"Humidity: {humidity}%."
        )
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return f"Error fetching weather for {city}: {str(e)}"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_forecast(city: str):
    """
    Get the 5-day weather forecast for a given city.
    
    Args:
        city: The name of the city.
    """
    logger.info(f"Fetching forecast for {city}")
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # Summarize forecast: Group by day
        forecasts = {}
        for item in data['list']:
            dt_txt = item['dt_txt'] # "2026-02-06 12:00:00"
            date = dt_txt.split(" ")[0]
            if date not in forecasts:
                forecasts[date] = []
            forecasts[date].append(item)
            
        summary = []
        for date, items in list(forecasts.items())[:3]: # Limit to 3 days to save tokens
            temps = [x['main']['temp'] for x in items]
            descs = [x['weather'][0]['description'] for x in items]
            # Most common description
            most_common_desc = max(set(descs), key=descs.count)
            avg_temp = sum(temps) / len(temps)
            summary.append(f"{date}: {most_common_desc}, Avg Temp: {avg_temp:.1f}°C")
            
        return f"3-Day Forecast for {city}:\n" + "\n".join(summary)

    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        return f"Error fetching forecast for {city}: {str(e)}"
