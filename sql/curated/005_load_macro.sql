-- Add any FRED dates that are not already in the shared date dimension

INSERT INTO curated.dim_date (
    date_key,
    full_date,
    year,
    month,
    day,
    quarter
)
SELECT DISTINCT
    TO_CHAR(observation_date, 'YYYYMMDD')::INTEGER,
    observation_date,
    EXTRACT(YEAR FROM observation_date)::INTEGER,
    EXTRACT(MONTH FROM observation_date)::INTEGER,
    EXTRACT(DAY FROM observation_date)::INTEGER,
    EXTRACT(QUARTER FROM observation_date)::INTEGER
FROM raw.fred_observations
ON CONFLICT (date_key) DO NOTHING;


-- Define the seven macroeconomic series

INSERT INTO curated.dim_macro_series (
    series_id,
    series_name,
    category,
    frequency
)
VALUES
    ('FEDFUNDS', 'Effective Federal Funds Rate', 'Monetary Policy', 'Monthly'),
    ('CPIAUCSL', 'Consumer Price Index', 'Inflation', 'Monthly'),
    ('UNRATE', 'Unemployment Rate', 'Labour Market', 'Monthly'),
    ('GS10', '10-Year Treasury Rate', 'Interest Rates', 'Monthly'),
    ('INDPRO', 'Industrial Production Index', 'Real Economy', 'Monthly'),
    ('PAYEMS', 'Total Nonfarm Payrolls', 'Labour Market', 'Monthly'),
    ('M2SL', 'M2 Money Stock', 'Money Supply', 'Monthly')
ON CONFLICT (series_id) DO NOTHING;


-- Rebuild the macro fact table from the raw FRED observations

TRUNCATE TABLE curated.fact_macro;

INSERT INTO curated.fact_macro (
    date_key,
    macro_series_key,
    value
)
SELECT
    d.date_key,
    m.macro_series_key,
    r.value
FROM raw.fred_observations AS r
JOIN curated.dim_date AS d
    ON r.observation_date = d.full_date
JOIN curated.dim_macro_series AS m
    ON r.series_id = m.series_id;