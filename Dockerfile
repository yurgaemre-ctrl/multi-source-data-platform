FROM apache/airflow:3.3.1

USER airflow

RUN pip install --no-cache-dir \
    yfinance \
    python-dotenv \
    pytest