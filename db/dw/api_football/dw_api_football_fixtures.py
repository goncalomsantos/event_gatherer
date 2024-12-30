from typing import List

import json
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional
import psycopg2

# Assuming raw files directory
raw_dir = (
    Path(__file__).resolve().parent.parent.parent / "raw" / "api_football" / "files"
)

POSTGRES_URI = os.getenv("POSTGRES_URI")


class Fixture(BaseModel):
    api_id: int
    timezone: str
    date: str
    timestamp: int
    venue_api_id: Optional[int]
    league_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str

    @field_validator(
        "api_id", "venue_api_id", "league_id", "home_team_id", "away_team_id"
    )
    def validate_id(cls, value):
        if value < 0:
            raise ValueError("ID must be positive")
        return value

    @field_validator("api_id", "timezone", "home_team_name", "away_team_name")
    def validate_string(cls, value):
        if not value:
            raise ValueError("Field cannot be empty")
        return value


def store_fixtures_in_db(fixtures):
    conn = psycopg2.connect(POSTGRES_URI)
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO dw_api_football_fixtures (api_id, timezone, date, timestamp, venue_api_id, league_id, 
    home_team_id, home_team_name, away_team_id, away_team_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (api_id) DO NOTHING;
    """

    fixture_tuples = [
        (
            f.api_id,
            f.timezone,
            f.date,
            f.timestamp,
            f.venue_api_id,
            f.league_id,
            f.home_team_id,
            f.home_team_name,
            f.away_team_id,
            f.away_team_name,
        )
        for f in fixtures
    ]
    try:
        cursor.executemany(insert_query, fixture_tuples)
        conn.commit()
        print("Fixtures inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting fixtures: {e}")
    finally:
        cursor.close()
        conn.close()


def get_latest_files() -> List[str]:
    fixtures = []
    files = list(raw_dir.glob("fixtures_*.jsonl"))

    if not files:
        return None  # No files, start fresh

    dates_and_files = []
    for file_path in files:
        try:
            date_str = file_path.stem.split("_")[
                1
            ]  # Extract date part from filename (YYYY-MM-DD)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            dates_and_files.append(
                (date_obj, file_path)
            )  # Store date and filename together
        except Exception as e:
            print(f"Error parsing date from file {file_path}: {e}")

    if not dates_and_files:
        return None

    # Fetch the max date from the database
    conn = psycopg2.connect(POSTGRES_URI)
    cursor = conn.cursor()

    max_date_query = """
    SELECT MAX(date)
    FROM DW_API_FOOTBALL_FIXTURES;
    """

    try:
        cursor.execute(max_date_query)
        row = cursor.fetchone()
        max_date = row[0].date()
        # Fetch max date from the database (it should be a datetime object)
        latest_files = []
        if max_date:
            print(f"Max date from DB: {max_date.strftime('%Y-%m-%d')}")

            # Filter files where the file date is greater than the max_date
            latest_files = [
                file_path.name for date, file_path in dates_and_files if date > max_date
            ]
        else:
            latest_files = [file_path.name for date, file_path in dates_and_files]
        return latest_files  # Return the filenames that meet the condition
    except Exception as e:
        conn.rollback()
        print(f"Error querying max date: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def process_fixtures_files() -> None:
    fixtures = []
    fixtures_to_load = get_latest_files()
    if not fixtures_to_load:
        print("No fixtures to process to dw")
        return

    for fixture_day in fixtures_to_load:
        with open(raw_dir / fixture_day, "r") as file:
            for line in file:
                try:
                    # Parse JSON data
                    fixture_data = json.loads(line)

                    # Extract necessary fields from the fixture
                    fixture = Fixture(
                        api_id=fixture_data["fixture"]["id"],
                        timezone=fixture_data["fixture"]["timezone"],
                        date=fixture_data["fixture"]["date"],
                        timestamp=fixture_data["fixture"]["timestamp"],
                        venue_api_id=(
                            fixture_data["fixture"]["venue"]["id"]
                            if fixture_data["fixture"]["venue"]
                            else None
                        ),
                        league_id=fixture_data["league"]["id"],
                        home_team_id=fixture_data["teams"]["home"]["id"],
                        home_team_name=fixture_data["teams"]["home"]["name"],
                        away_team_id=fixture_data["teams"]["away"]["id"],
                        away_team_name=fixture_data["teams"]["away"]["name"],
                    )

                    # Add valid fixture to the list
                    fixtures.append(fixture)

                except ValidationError as e:
                    print(f"Validation failed for fixture: {e}")
                except Exception as e:
                    print(f"Error processing fixture: {e}")

    # Store all valid fixtures into the database
    store_fixtures_in_db(fixtures)


# Run the process to read fixtures and store them
process_fixtures_files()
