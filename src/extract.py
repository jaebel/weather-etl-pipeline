import requests
import yaml
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv() # This and the dotenv import work fine despite weird highlighting

def load_config():
    """Load configuration from YAML file"""
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def fetch_weather_data(lat, lon):
    """Fetch weather data from RapidAPI for given coordinates"""
    api_key = os.getenv('RAPIDAPI_KEY')
    
    url = "https://weatherbit-v1-mashape.p.rapidapi.com/forecast/daily"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "weatherbit-v1-mashape.p.rapidapi.com"
    }
    
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "lang": "en"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception if you get 4 or 5 hundreds codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def save_raw_data(data, city_name):
    """Save raw API response to file for debugging"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"logs/{city_name}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved raw data to {filename}")

def main():
    """Main - extracting and storing data from weather api for each city"""
    config = load_config()
    
    for city in config['cities']:
        print(f"\nFetching weather data for {city['name']}...")
        
        weather_data = fetch_weather_data(city['lat'], city['lon'])
        
        if weather_data:
            save_raw_data(weather_data, city['name'])
            print(f"✓ Successfully fetched data for {city['name']}")
        else:
            print(f"✗ Failed to fetch data for {city['name']}")

if __name__ == "__main__":
    main()