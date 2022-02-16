CREATE TABLE IF NOT EXISTS stock_data(
    date       DATE NOT NULL,
    open       NUMERIC,
    high       NUMERIC,
    low        NUMERIC,
    close      NUMERIC,
    volume     NUMERIC,
    Ticker     VARCHAR(5) NOT NULL
);