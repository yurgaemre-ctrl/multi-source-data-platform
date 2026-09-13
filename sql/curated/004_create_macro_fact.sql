CREATE TABLE IF NOT EXISTS curated.dim_macro_series (
    macro_series_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    series_id TEXT UNIQUE NOT NULL,
    series_name TEXT NOT NULL,
    category TEXT NOT NULL,
    frequency TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS curated.fact_macro (
    date_key INTEGER NOT NULL,
    macro_series_key INTEGER NOT NULL,
    value NUMERIC,

    PRIMARY KEY (date_key, macro_series_key),

    FOREIGN KEY (date_key)
        REFERENCES curated.dim_date(date_key),

    FOREIGN KEY (macro_series_key)
        REFERENCES curated.dim_macro_series(macro_series_key)
);