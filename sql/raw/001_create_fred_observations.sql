CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.fred_observations (
    series_id TEXT,
    observation_date DATE,
    value NUMERIC,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);