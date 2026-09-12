import os

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES_ID = "FEDFUNDS"

url = "https://api.stlouisfed.org/fred/series/observations"

params = {
    "series_id": SERIES_ID,
    "api_key": FRED_API_KEY,
    "file_type": "json",
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

observations = response.json()["observations"]

rows = [
    (SERIES_ID, observation["date"], observation["value"])
    for observation in observations
    if observation["value"] != "."
]

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="platform",
    user="platform_user",
    password="platform_password",
) as connection:

    with connection.cursor() as cursor:

        cursor.execute(
            "DELETE FROM raw.fred_observations WHERE series_id = %s",
            (SERIES_ID,),
        )

        cursor.executemany(
            """
            INSERT INTO raw.fred_observations
                (series_id, observation_date, value)
            VALUES (%s, %s, %s)
            """,
            rows,
        )

print(f"Loaded {len(rows)} observations for {SERIES_ID}")