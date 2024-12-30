import requests
import os

from dotenv import load_dotenv

# poetry run python .\tests\api_football_connection.py

load_dotenv()

API_SPORTS_API_KEY = os.getenv("API_SPORTS_API_KEY")

url = "https://v3.football.api-sports.io/"
headers = {
    "x-rapidapi-key": API_SPORTS_API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io",
}

response = requests.get(f"{url}status", headers=headers)


# Check the response status and print the data
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
