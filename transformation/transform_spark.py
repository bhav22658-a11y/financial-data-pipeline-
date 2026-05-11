from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, LongType
import os

spark = SparkSession.builder \
    .appName("NSE_Trade_Pipeline") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")


def load_raw(path="data/raw_trades.csv"):
    df = spark.read.csv(path, header=True, inferSchema=True)
    print(f"Raw records loaded: {df.count():,}")
    return df


def transform(df):
    # Step 1: Explicit type casting — prevents silent aggregation errors
    df = df \
        .withColumn("OPEN",       F.col("OPEN").cast(DoubleType())) \
        .withColumn("HIGH",       F.col("HIGH").cast(DoubleType())) \
        .withColumn("LOW",        F.col("LOW").cast(DoubleType()))  \
        .withColumn("CLOSE",      F.col("CLOSE").cast(DoubleType())) \
        .withColumn("TOTTRDQTY",  F.col("TOTTRDQTY").cast(LongType()))

    # Step 2: Deduplicate
    before = df.count()
    df = df.dropDuplicates(["SYMBOL", "TIMESTAMP"])
    print(f"Duplicates removed: {before - df.count():,}")

    # Step 3: Drop nulls in key columns
    df = df.dropna(subset=["SYMBOL", "CLOSE", "TOTTRDQTY"])
    print(f"Clean records: {df.count():,}")
    return df


def build_reporting(df):
    return df.groupBy("SYMBOL") \
        .agg(
            F.round(F.avg("CLOSE"), 2).alias("avg_close"),
            F.max("HIGH").alias("day_high"),
            F.min("LOW").alias("day_low"),
            F.sum("TOTTRDQTY").alias("total_volume"),
            F.count("*").alias("trade_count")
        ) \
        .orderBy("total_volume", ascending=False)


def save_layers(df_raw, df_clean, df_report):
    for path in ["data/raw/", "data/transformed/", "data/reporting/"]:
        os.makedirs(path, exist_ok=True)
    df_raw.write.mode("overwrite").parquet("data/raw/")
    df_clean.write.mode("overwrite").parquet("data/transformed/")
    df_report.write.mode("overwrite").parquet("data/reporting/")
    print("All 3 layers saved successfully.")


if __name__ == "__main__":
    df_raw    = load_raw()
    df_clean  = transform(df_raw)
    df_report = build_reporting(df_clean)
    df_report.show()
    save_layers(df_raw, df_clean, df_report)
