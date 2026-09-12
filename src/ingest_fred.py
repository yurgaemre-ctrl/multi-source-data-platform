import os

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES_IDS = [
    "FEDFUNDS",   # Effective Federal Funds Rate
    "CPIAUCSL",   # Consumer Price Index
    "UNRATE",     # Unemployment Rate
    "GS10",       # 10-Year Treasury Rate
    "INDPRO",     # Industrial Production Index
    "PAYEMS",     # Total Nonfarm Payrolls
    "M2SL",       # M2 Money Stock
]

url = "https://api.stlouisfed.org/fred/series/observations"

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="platform",
    user="platform_user",
    password="platform_password",
) as connection:

    with connection.cursor() as cursor:

        for series_id in SERIES_IDS:

            params = {
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json",
            }

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            observations = response.json()["observations"]

            rows = [
                (
                    series_id,
                    observation["date"],
                    observation["value"],
                )
                for observation in observations
                if observation["value"] != "."
            ]

            cursor.execute(
                """
                DELETE FROM raw.fred_observations
                WHERE series_id = %s
                """,
                (series_id,),
            )

            cursor.executemany(
                """
                INSERT INTO raw.fred_observations
                    (series_id, observation_date, value)
                VALUES (%s, %s, %s)
                """,
                rows,
            )

            print(
                f"Loaded {len(rows)} observations for {series_id}"
            )