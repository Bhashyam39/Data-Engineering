# Week 1: SQL Foundations + Python API Script

## What I Learned This Week
- SQL: SELECT, WHERE, JOINs, NULL handling, Aggregation, Subqueries
- Python: Fetching data from APIs, writing to CSV, logging, error handling

## Files in This Folder

| File | Description |
|------|-------------|
| `sql_notes.md` | Digital SQL notes |
| `sql_notes_page*.jpg` | Handwritten SQL notes |
| `weather.py` | Fetches weather data from Open-Meteo API and saves to CSV |

## How to Run the Weather Script

```bash
# Install dependency
pip install requests

# Run the script
python weather.py

# Output: Creates weather_YYYY-MM-DD.csv