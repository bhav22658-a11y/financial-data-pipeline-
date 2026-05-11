import pandas as pd
import numpy as np
import os

# ── Generates 500K synthetic NSE-style trade records ──
# Fallback used when live NSE data is unavailable

def generate_sample_data():
    n = 500_000
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
               "WIPRO", "AXISBANK", "LT", "SBIN", "BAJFINANCE"] * (n // 10)

    np.random.seed(42)
    df = pd.DataFrame({
        "SYMBOL":    symbols,
        "SERIES":    "EQ",
        "OPEN":      np.random.uniform(100, 4000, n).round(2),
        "HIGH":      np.random.uniform(100, 4200, n).round(2),
        "LOW":       np.random.uniform(80,  3900, n).round(2),
        "CLOSE":     np.random.uniform(100, 4000, n).round(2),
        "TOTTRDQTY": np.random.randint(1000, 500000, n),
        "TOTTRDVAL": np.random.uniform(1e6, 1e9, n).round(2),
        "TIMESTAMP": pd.date_range("2024-01-01", periods=n, freq="1min")
    })

    # Inject duplicates and nulls to make transformation steps meaningful
    duplicates = df.sample(500, random_state=1)
    df = pd.concat([df, duplicates], ignore_index=True)

    null_indices = np.random.choice(df.index, 200, replace=False)
    df.loc[null_indices, "CLOSE"] = None

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_trades.csv", index=False)
    print(f"Generated {len(df):,} records → data/raw_trades.csv")
    return df


if __name__ == "__main__":
    df = generate_sample_data()
    print(df.head(3))
