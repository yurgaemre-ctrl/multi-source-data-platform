TRUNCATE TABLE curated.fact_market;

INSERT INTO curated.fact_market (
    date_key,
    asset_key,
    source,
    open,
    high,
    low,
    close,
    adjusted_close,
    volume
)
SELECT
    d.date_key,
    a.asset_key,
    s.source,
    s.open,
    s.high,
    s.low,
    s.close,
    s.adjusted_close,
    s.volume
FROM staging.market_prices AS s
JOIN curated.dim_date AS d
    ON s.price_date = d.full_date
JOIN curated.dim_asset AS a
    ON s.symbol = a.symbol;