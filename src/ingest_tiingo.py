import os

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

TIINGO_API_KEY = os.getenv("TIINGO_API_KEY")

SYMBOLS = [
    "SPY",
    "QQQ",
]

START_DATE = "2000-01-01"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Token {TIINGO_API_KEY}",
}

with psycopg.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB", "platform"),
    user=os.getenv("POSTGRES_USER", "platform_user"),
    password=os.environ["POSTGRES_PASSWORD"],
) as connection:

    with connection.cursor() as cursor:

        for symbol in SYMBOLS:

            url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices"

            params = {
                "startDate": START_DATE,
                "resampleFreq": "daily",
            }

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            observations = response.json()

            rows = [
                (
                    symbol,
                    observation["date"][:10],
                    observation["open"],
                    observation["high"],
                    observation["low"],
                    observation["close"],
                    observation["adjClose"],
                    observation["volume"],
                )
                for observation in observations
            ]

            cursor.execute(
                """
                DELETE FROM raw.tiingo_prices
                WHERE symbol = %s
                """,
                (symbol,),
            )

            cursor.executemany(
                """
                INSERT INTO raw.tiingo_prices (
                    symbol,
                    price_date,
                    open,
                    high,
                    low,
                    close,
                    adjusted_close,
                    volume
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )

            print(f"Loaded {len(rows)} observations for {symbol}")