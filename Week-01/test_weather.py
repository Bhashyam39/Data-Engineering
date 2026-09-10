import requests
from unittest.mock import patch, MagicMock
from weather import fetch_weather

def test_fetch_weather_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "daily": {
            "time": ["2026-09-10"],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [18.0]
        }
    }
    
    with patch('weather.requests.get', return_value=mock_response):
        result = fetch_weather("TestCity", 0, 0)
        assert len(result) == 1
        assert result[0]["city"] == "TestCity"
        assert result[0]["max_temp"] == 25.0

def test_fetch_weather_failure():
    with patch('weather.requests.get', side_effect=requests.RequestException("API down")):
        result = fetch_weather("TestCity", 0, 0)
        assert result == []