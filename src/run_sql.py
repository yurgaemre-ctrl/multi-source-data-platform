import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import psycopg


def run_sql_file(sql_file):
    sql_path = Path(sql_file)

    with psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "platform"),
        user=os.getenv("POSTGRES_USER", "platform_user"),
        password=os.environ["POSTGRES_PASSWORD"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_path.read_text())

    print(f"Successfully executed {sql_path}")


if __name__ == "__main__":
    run_sql_file(sys.argv[1])
