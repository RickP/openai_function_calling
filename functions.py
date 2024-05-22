from datetime import datetime
from generate_json import generate_json
import requests

openmeteo_url = "https://api.open-meteo.com/v1/forecast"

@generate_json
def get_date() -> str:
    """Return the current date in the format Weekday - YYYY-MM-DD
    """
    return datetime.now().strftime("%A %Y-%m-%d")

@generate_json
def get_time() -> str:
    """Return the current time in the format HH:MM
    """
    return datetime.now().strftime("%H:%M")

@generate_json
def get_weather_for_location(lat: float, lon: float) -> str:
    """Return the weather forecast for the next 7 days for a specific location. Returns a table with the columns
    date, time, temperature, rainfall
    there will be a row for every hour in the next 7 days starting with the next hour.
    :param lat: float: The latitude of the location
    :param lon: float: The longitude of the location
    """
    request_url = openmeteo_url + "?latitude=" + str(lat) + "&longitude=" + str(lon) + "&hourly=temperature_2m,rain"
    response = requests.get(request_url).json()
    
    ret = ""
    index = 0
    for time in response['hourly']['time']:
        ret += "date: " + time[0:10] + ", time: " + time[11:16] + ", temperature: " + str(response['hourly']['temperature_2m'][index]) + ", rainfall: " + str(response['hourly']['rain'][index]) + "\n"
        index += 1
    return ret