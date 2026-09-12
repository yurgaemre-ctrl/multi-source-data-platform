TRUNCATE TABLE staging.market_prices;

INSERT INTO staging.market_prices (
    source,
    symbol,
    price_date,
    open,
    high,
    low,
    close,
    adjusted_close,
    volume
)
SELECT
    'yahoo',
    symbol,
    price_date,
    open,
    high,
    low,
    close,
    adjusted_close,
    volume
FROM raw.yahoo_prices;

INSERT INTO staging.market_prices (
    source,
    symbol,
    price_date,
    open,
    high,
    low,
    close,
    adjusted_close,
    volume
)
SELECT
    'tiingo',
    symbol,
    price_date,
    open,
    high,
    low,
    close,
    adjusted_close,
    volume
FROM raw.tiingo_prices;