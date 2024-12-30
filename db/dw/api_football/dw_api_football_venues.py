from typing import Optional
import json
import os
from pathlib import Path
from pydantic import field_validator, BaseModel, ValidationError, Field
import psycopg2


# Directory path
raw_dir = (
    Path(__file__).resolve().parent.parent.parent / "raw" / "api_football" / "files"
)

POSTGRES_URI = os.getenv("POSTGRES_URI")


class Venue(BaseModel):
    api_id: int = Field(alias="id")
    address: Optional[str]
    name: str
    city: Optional[str]
    country: Optional[str]
    source_api: str  # Add source API field to the model

    @field_validator("api_id")
    def validate_api_id(cls, value):
        if value < 0:
            raise ValueError("API ID can't be lower than 0")
        return value


def store_venues_in_dw(venues: list) -> None:
    conn = psycopg2.connect(POSTGRES_URI)
    cur = conn.cursor()

    query = """
    INSERT INTO app_venues (api_id, address, name, city, country, source_api)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (api_id) DO NOTHING;
    """

    values = [
        (
            venue.api_id,
            venue.address,
            venue.name,
            venue.city,
            venue.country,
            venue.source_api,
        )
        for venue in venues
    ]

    try:
        cur.executemany(query, values)
        conn.commit()
    except Exception as e:
        print(f"Error inserting venues: {e}")
    finally:
        cur.close()
        conn.close()


def process_venues_file(source_api: str) -> None:
    venues = []

    with open(raw_dir / "venues.jsonl", "r") as file:
        for line in file:
            try:
                venue_data = json.loads(line)
                venue_data["source_api"] = source_api  # Add source API to the data

                # Validate and create a Venue object
                venue = Venue(**venue_data)
                venues.append(venue)
            except ValidationError as e:
                print(f"Validation failed for venue: {e}")
            except Exception as e:
                print(f"Error processing venue: {e}")

    if venues:
        store_venues_in_dw(venues)


# Example call: process venues from the football API
process_venues_file("api_football")
