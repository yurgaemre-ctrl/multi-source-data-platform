import psycopg
import yfinance as yf

SYMBOLS = [
    "SPY",      # S&P 500 ETF
    "QQQ",      # Nasdaq-100 ETF
    "^VIX",     # CBOE Volatility Index
]

START_DATE = "2000-01-01"

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="platform",
    user="platform_user",
    password="platform_password",
) as connection:

    with connection.cursor() as cursor:

        for symbol in SYMBOLS:

            data = yf.download(
                symbol,
                start=START_DATE,
                auto_adjust=False,
                progress=False,
            )

            rows = []

            for date, row in data.iterrows():

                rows.append(
                    (
                        symbol,
                        date.date(),
                        float(row["Open"].iloc[0]),
                        float(row["High"].iloc[0]),
                        float(row["Low"].iloc[0]),
                        float(row["Close"].iloc[0]),
                        float(row["Adj Close"].iloc[0]),
                        int(row["Volume"].iloc[0]),
                    )
                )

            cursor.execute(
                """
                DELETE FROM raw.yahoo_prices
                WHERE symbol = %s
                """,
                (symbol,),
            )

            cursor.executemany(
                """
                INSERT INTO raw.yahoo_prices (
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