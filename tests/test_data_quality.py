import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "platform"),
        user=os.getenv("POSTGRES_USER", "platform_user"),
        password=os.environ["POSTGRES_PASSWORD"],
    )


def test_market_primary_keys_are_not_null():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM curated.fact_market
                WHERE date_key IS NULL
                   OR asset_key IS NULL
                   OR source IS NULL
                """
            )

            null_count = cursor.fetchone()[0]

    assert null_count == 0


def test_macro_primary_keys_are_not_null():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM curated.fact_macro
                WHERE date_key IS NULL
                   OR macro_series_key IS NULL
                """
            )

            null_count = cursor.fetchone()[0]

    assert null_count == 0


def test_market_prices_are_positive():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM curated.fact_market
                WHERE adjusted_close <= 0
                """
            )

            invalid_count = cursor.fetchone()[0]

    assert invalid_count == 0


def test_expected_macro_series_exist():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM curated.dim_macro_series
                """
            )

            series_count = cursor.fetchone()[0]

    assert series_count == 7
