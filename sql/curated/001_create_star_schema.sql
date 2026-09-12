CREATE SCHEMA IF NOT EXISTS curated;

CREATE TABLE IF NOT EXISTS curated.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    quarter INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS curated.dim_asset (
    asset_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    asset_name TEXT,
    asset_type TEXT
);

CREATE TABLE IF NOT EXISTS curated.fact_market (
    date_key INTEGER NOT NULL,
    asset_key INTEGER NOT NULL,
    source TEXT NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    adjusted_close NUMERIC,
    volume BIGINT,

    PRIMARY KEY (date_key, asset_key, source),

    FOREIGN KEY (date_key)
        REFERENCES curated.dim_date(date_key),

    FOREIGN KEY (asset_key)
        REFERENCES curated.dim_asset(asset_key)
);