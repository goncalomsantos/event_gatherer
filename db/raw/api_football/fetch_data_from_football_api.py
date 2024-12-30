from typing import List, Dict, Optional, Callable, Union

from datetime import datetime, timedelta
import os
import requests
import json
from collections import defaultdict
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

API_SPORTS_API_KEY = os.getenv("API_SPORTS_API_KEY")

url = "https://v3.football.api-sports.io"
headers = {
    "x-rapidapi-key": API_SPORTS_API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io",
}

# Get the relative file path using pathlib
save_dir = Path(__file__).resolve().parent / "files"

# Ensure the directory exists
save_dir.mkdir(parents=True, exist_ok=True)


# Function to fetch events from Eventbrite API
def fetch_leagues() -> Optional[Dict]:
    response = requests.get(url=f"{url}/leagues?current=true&code=pt", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching leagues: {response.status_code}")
        return None


def fetch_venues() -> Optional[Dict]:
    # TODO: check if country is in country options of leagues
    response = requests.get(url=f"{url}/venues?country=portugal", headers=headers)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        print(f"Error fetching venues: {response.status_code}")
        return None


def get_last_saved_date() -> Optional[datetime]:
    """Find the latest date from the saved JSONL files using pathlib."""
    if not save_dir.exists():
        return None  # No files, start fresh

    files = list(save_dir.glob("fixtures_*.jsonl"))

    if not files:
        return None  # No files, start fresh

    # Extract dates from filenames
    dates = []
    for file_path in files:
        try:
            date_str = file_path.stem.split("_")[
                1
            ]  # Extract date part from the filename (YYYY-MM-DD)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            dates.append(date_obj)
        except Exception as e:
            print(f"Error parsing date from file {file_path}: {e}")

    if not dates:
        return None

    # Return the latest date
    return max(dates)


def fetch_games_in_30_days() -> Optional[Dict]:

    last_saved_date = get_last_saved_date()

    if last_saved_date:
        start_date = last_saved_date
    else:
        start_date = datetime(2022, 11, 1)

    # we are simulating processing day as 2022-11-01
    # in the future we will not return whole json
    # but instead pages because dataset may be
    # too large. in that case, if process fails
    # we merge datapoints using fixture id
    # so that we dont get duplicates
    today = datetime(2022, 11, 1)

    current_year = today.year

    last_day = today + timedelta(30)

    start_date = start_date.strftime("%Y-%m-%d")
    last_date = last_day.strftime("%Y-%m-%d")
    print("Start date:", start_date)
    print("Last day of the week:", last_date)

    # TODO: add filter league universe where league in leagues.jsonl
    response = requests.get(
        url=f"{url}/fixtures?league=94&season={current_year}"
        f"&from={start_date}&to={last_date}",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching games: {response.status_code}")
        return None


def save_monthly_fixtures(api_data: Dict) -> None:
    # Group data by date
    # defaultdict creates the key if it doesnt exist
    fixtures_by_date = defaultdict(list)

    for fixture in api_data["response"]:
        # Extract the date from the fixture's 'date' field (only the YYYY-MM-DD part)
        fixture_date = fixture["fixture"]["date"][:10]
        fixtures_by_date[fixture_date].append(fixture)

    # Save each day's fixtures to a separate JSONL file
    for fixture_date, fixtures in fixtures_by_date.items():
        save_to_jsonl(data=fixtures, filename=f"fixtures_{fixture_date}")


# Function to save data to a .jsonl file
def save_to_jsonl(data: Union[Dict, List], filename: str = "leagues") -> None:
    file_path = save_dir / f"{filename}.jsonl"

    with open(file_path, "w") as file:
        for item in data:
            # Write each item as a new line (JSON object)
            try:
                json.dump(item, file)
                file.write("\n")
            except Exception as e:
                print(e)


# Main function to run the data collection and insertion
def main() -> None:
    data = fetch_games_in_30_days()
    save_monthly_fixtures(data)
    # save_to_jsonl(data, "venues")


if __name__ == "__main__":
    main()
