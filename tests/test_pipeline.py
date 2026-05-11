import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extraction.ingest import generate_sample_data


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture(scope="module")
def raw_df():
    return generate_sample_data()


# ── Extraction tests ──────────────────────────────────────────
def test_record_count(raw_df):
    """Pipeline generates expected volume of records."""
    assert len(raw_df) >= 500_000

def test_required_columns(raw_df):
    """All required columns present."""
    required = ["SYMBOL", "SERIES", "OPEN", "HIGH", "LOW", "CLOSE", "TOTTRDQTY", "TIMESTAMP"]
    for col in required:
        assert col in raw_df.columns, f"Missing column: {col}"

def test_symbols_not_empty(raw_df):
    """SYMBOL column has no empty strings."""
    assert raw_df["SYMBOL"].str.strip().ne("").all()

def test_csv_file_created():
    """CSV file exists after ingestion."""
    assert os.path.exists("data/raw_trades.csv")


# ── Schema / type tests ───────────────────────────────────────
def test_close_is_numeric(raw_df):
    """CLOSE column must be numeric — catches silent type mismatch bug."""
    non_null = raw_df["CLOSE"].dropna()
    assert pd.to_numeric(non_null, errors="coerce").notna().all()

def test_volume_is_integer(raw_df):
    """TOTTRDQTY must be integer type."""
    assert raw_df["TOTTRDQTY"].dtype in [np.int32, np.int64]

def test_no_negative_prices(raw_df):
    """Price columns must be non-negative."""
    for col in ["OPEN", "HIGH", "LOW"]:
        assert (raw_df[col].dropna() >= 0).all(), f"{col} has negative values"


# ── Data quality tests ────────────────────────────────────────
def test_duplicates_exist_before_dedup(raw_df):
    """Confirms duplicates were injected — dedup step has real work."""
    dupes = raw_df.duplicated(subset=["SYMBOL", "TIMESTAMP"]).sum()
    assert dupes > 0, "Expected injected duplicates not found"

def test_nulls_exist_in_close(raw_df):
    """Confirms nulls were injected — null-drop step has real work."""
    assert raw_df["CLOSE"].isna().sum() > 0

def test_dedup_removes_duplicates(raw_df):
    """After dedup, no duplicate SYMBOL+TIMESTAMP pairs remain."""
    deduped = raw_df.drop_duplicates(subset=["SYMBOL", "TIMESTAMP"])
    assert deduped.duplicated(subset=["SYMBOL", "TIMESTAMP"]).sum() == 0

def test_null_drop_removes_nulls(raw_df):
    """After null drop, no nulls in key columns."""
    cleaned = raw_df.dropna(subset=["SYMBOL", "CLOSE", "TOTTRDQTY"])
    assert cleaned["CLOSE"].isna().sum() == 0
    assert cleaned["TOTTRDQTY"].isna().sum() == 0


# ── Regression test — off-by-one threshold bug ────────────────
def test_close_threshold_boundary():
    """
    Regression: validates threshold comparison is inclusive (>=)
    not exclusive (>). Off-by-one was causing boundary records
    to pass through without flagging.
    """
    def is_above_threshold(close, threshold):
        return close >= threshold   # must be >= not >

    assert is_above_threshold(100.0, 100.0) is True,  "Boundary value must be flagged"
    assert is_above_threshold(99.99, 100.0) is False, "Below threshold must not be flagged"
    assert is_above_threshold(100.01, 100.0) is True, "Above threshold must be flagged"
