import requests
import csv
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_weather(city, lat, lon, days=7):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
        "forecast_days": days
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = []
        for i, date in enumerate(data["daily"]["time"]):
            results.append({
                "date": date,
                "city": city,
                "max_temp": data["daily"]["temperature_2m_max"][i],
                "min_temp": data["daily"]["temperature_2m_min"][i]
            })
        return results
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {city}: {e}")
        return []

def save_to_csv(data, filename):
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = Path(f"{filename}_{today}.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "city", "max_temp", "min_temp"])
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Saved {len(data)} rows to {filepath}")
    return filepath

def main():
    cities = [
        {"name": "New York", "lat": 40.71, "lon": -74.01},
        {"name": "London", "lat": 51.51, "lon": -0.13},
        {"name": "Tokyo", "lat": 35.68, "lon": 139.69},
    ]
    all_weather = []
    for city in cities:
        weather = fetch_weather(city["name"], city["lat"], city["lon"])
        all_weather.extend(weather)
    save_to_csv(all_weather, "weather")
    print(f"Fetched {len(all_weather)} rows total.")

if __name__ == "__main__":
    main()
