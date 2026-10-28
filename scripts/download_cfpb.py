import os
import sys
import urllib.request
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

TRAIN_PARQUET_PATH = os.path.join(RAW_DIR, "cfpb_train.parquet")
TEST_PARQUET_PATH = os.path.join(RAW_DIR, "cfpb_test.parquet")
TRAIN_CSV_PATH = os.path.join(RAW_DIR, "train.csv")
TEST_CSV_PATH = os.path.join(RAW_DIR, "test.csv")


def extract_splits(sample_train: int = 40000, sample_test: int = 10000):
    print("Reading local CFPB Parquet files...")
    train_df = pd.read_parquet(TRAIN_PARQUET_PATH)
    test_df = pd.read_parquet(TEST_PARQUET_PATH)

    rename_map = {
        'Consumer Complaint': 'Consumer complaint narrative',
        'Company Public Response': 'Company public response',
        'Date Sent to Company': 'Date sent to company',
        'Company Response to Consumer': 'Company response to consumer'
    }
    train_df.rename(columns=rename_map, inplace=True)
    test_df.rename(columns=rename_map, inplace=True)

    # Filter out empty narratives
    train_df = train_df.dropna(subset=['Consumer complaint narrative', 'Product'])
    test_df = test_df.dropna(subset=['Consumer complaint narrative', 'Product'])

    print(f"Total valid complaints: {len(train_df):,} train, {len(test_df):,} test")

    # Sample without losing Product column
    if len(train_df) > sample_train:
        train_sampled = train_df.sample(n=sample_train, random_state=42)
    else:
        train_sampled = train_df

    if len(test_df) > sample_test:
        test_sampled = test_df.sample(n=sample_test, random_state=42)
    else:
        test_sampled = test_df

    train_sampled.to_csv(TRAIN_CSV_PATH, index=False)
    test_sampled.to_csv(TEST_CSV_PATH, index=False)
    print(f"Saved {len(train_sampled):,} complaints to {TRAIN_CSV_PATH}")
    print(f"Saved {len(test_sampled):,} complaints to {TEST_CSV_PATH}")
    print("Columns in train.csv:", train_sampled.columns.tolist()[:8])


if __name__ == "__main__":
    extract_splits()
