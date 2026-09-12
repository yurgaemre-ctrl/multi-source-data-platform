INSERT INTO curated.dim_date (
    date_key,
    full_date,
    year,
    month,
    day,
    quarter
)
SELECT DISTINCT
    TO_CHAR(price_date, 'YYYYMMDD')::INTEGER AS date_key,
    price_date AS full_date,
    EXTRACT(YEAR FROM price_date)::INTEGER AS year,
    EXTRACT(MONTH FROM price_date)::INTEGER AS month,
    EXTRACT(DAY FROM price_date)::INTEGER AS day,
    EXTRACT(QUARTER FROM price_date)::INTEGER AS quarter
FROM staging.market_prices
ON CONFLICT (date_key) DO NOTHING;


INSERT INTO curated.dim_asset (
    symbol,
    asset_name,
    asset_type
)
VALUES
    ('SPY', 'SPDR S&P 500 ETF Trust', 'ETF'),
    ('QQQ', 'Invesco QQQ Trust', 'ETF'),
    ('^VIX', 'CBOE Volatility Index', 'Index')
ON CONFLICT (symbol) DO NOTHING;