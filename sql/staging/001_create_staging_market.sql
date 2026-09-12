CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.market_prices (
    source TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price_date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    adjusted_close NUMERIC,
    volume BIGINT,
    PRIMARY KEY (source, symbol, price_date)
);