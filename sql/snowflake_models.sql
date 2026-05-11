-- ─────────────────────────────────────────────────────
-- Snowflake 3-Layer Data Model
-- financial-data-pipeline
-- ─────────────────────────────────────────────────────

-- ── RAW LAYER ─────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS TRADE_DB;
CREATE SCHEMA IF NOT EXISTS TRADE_DB.RAW;

CREATE TABLE IF NOT EXISTS TRADE_DB.RAW.NSE_TRADES (
    SYMBOL      VARCHAR(20),
    SERIES      VARCHAR(5),
    OPEN        FLOAT,
    HIGH        FLOAT,
    LOW         FLOAT,
    CLOSE       FLOAT,
    TOTTRDQTY   BIGINT,
    TOTTRDVAL   FLOAT,
    TIMESTAMP   TIMESTAMP,
    LOADED_AT   TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ── TRANSFORMED LAYER ─────────────────────────────────
CREATE SCHEMA IF NOT EXISTS TRADE_DB.TRANSFORMED;

CREATE TABLE IF NOT EXISTS TRADE_DB.TRANSFORMED.NSE_TRADES_CLEAN (
    SYMBOL      VARCHAR(20),
    SERIES      VARCHAR(5),
    OPEN        FLOAT,
    HIGH        FLOAT,
    LOW         FLOAT,
    CLOSE       FLOAT,
    TOTTRDQTY   BIGINT,
    TOTTRDVAL   FLOAT,
    TIMESTAMP   TIMESTAMP
)
CLUSTER BY (SYMBOL);  -- clustering key for query optimisation

-- ── REPORTING LAYER ───────────────────────────────────
CREATE SCHEMA IF NOT EXISTS TRADE_DB.REPORTING;

CREATE TABLE IF NOT EXISTS TRADE_DB.REPORTING.SYMBOL_DAILY_SUMMARY (
    SYMBOL          VARCHAR(20),
    AVG_CLOSE       FLOAT,
    DAY_HIGH        FLOAT,
    DAY_LOW         FLOAT,
    TOTAL_VOLUME    BIGINT,
    TRADE_COUNT     BIGINT,
    CREATED_AT      TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (SYMBOL);

-- ── STORED PROCEDURE: Reconciliation ─────────────────
CREATE OR REPLACE PROCEDURE TRADE_DB.REPORTING.RECONCILE_LAYERS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    raw_count       INTEGER;
    clean_count     INTEGER;
    report_count    INTEGER;
    result          STRING;
BEGIN
    SELECT COUNT(*) INTO raw_count   FROM TRADE_DB.RAW.NSE_TRADES;
    SELECT COUNT(*) INTO clean_count FROM TRADE_DB.TRANSFORMED.NSE_TRADES_CLEAN;
    SELECT COUNT(*) INTO report_count FROM TRADE_DB.REPORTING.SYMBOL_DAILY_SUMMARY;

    result := 'RAW: ' || raw_count ||
              ' | TRANSFORMED: ' || clean_count ||
              ' | REPORTING: ' || report_count ||
              ' | Drop rate: ' || ROUND((1 - clean_count/raw_count) * 100, 2) || '%';
    RETURN result;
END;
$$;

-- ── STORED PROCEDURE: Exception Report ───────────────
CREATE OR REPLACE PROCEDURE TRADE_DB.REPORTING.EXCEPTION_REPORT()
RETURNS TABLE (SYMBOL VARCHAR, ISSUE VARCHAR, RECORD_COUNT INTEGER)
LANGUAGE SQL
AS
$$
    SELECT SYMBOL, 'HIGH < LOW' AS ISSUE, COUNT(*) AS RECORD_COUNT
    FROM TRADE_DB.TRANSFORMED.NSE_TRADES_CLEAN
    WHERE HIGH < LOW
    GROUP BY SYMBOL
    HAVING COUNT(*) > 0
    ORDER BY RECORD_COUNT DESC;
$$;
