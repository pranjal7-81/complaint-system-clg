import csv
import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

TRAIN_DATA_PATH = os.path.join("data", "processed", "train.csv")
TEST_DATA_PATH = os.path.join("data", "processed", "test.csv")
ARTIFACTS_DIR = "artifacts"

VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.pkl")
METADATA_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_metadata.json")


def load_texts_and_labels(file_path: str):
    texts = []
    labels = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["category"])
    return texts, labels


def fit_and_transform_tfidf(
    max_features: int = 5000,
    ngram_range: tuple = (1, 2),
    min_df: int = 2
):
    print("=" * 60)
    print("        TF-IDF VECTORIZATION PIPELINE")
    print("=" * 60)

    print("\n1. Loading train and test data...")
    train_texts, train_labels = load_texts_and_labels(TRAIN_DATA_PATH)
    test_texts, test_labels = load_texts_and_labels(TEST_DATA_PATH)
    print(f"   - Train samples : {len(train_texts)}")
    print(f"   - Test samples  : {len(test_texts)}")

    print("\n2. Initializing TfidfVectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        stop_words="english",
        sublinear_tf=True
    )

    print("\n3. Fitting TF-IDF ONLY on training data (Strictly Zero Leakage)...")
    X_train = vectorizer.fit_transform(train_texts)
    print(f"   - X_train shape: {X_train.shape}")

    print("\n4. Transforming test data...")
    X_test = vectorizer.transform(test_texts)
    print(f"   - X_test shape : {X_test.shape}")

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"\n5. Saved vectorizer to: {VECTORIZER_PATH}")

    feature_names = vectorizer.get_feature_names_out().tolist()
    metadata = {
        "max_features": max_features,
        "ngram_range": list(ngram_range),
        "min_df": min_df,
        "vocabulary_size": len(feature_names),
        "train_samples": X_train.shape[0],
        "test_samples": X_test.shape[0],
        "sample_features": feature_names[:25]
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"6. Saved metadata to: {METADATA_PATH}")

    print("\nTop 20 vocabulary features:")
    print(feature_names[:20])
    print("\n" + "=" * 60)
    print("SUCCESS: TF-IDF vectorization completed!")
    print("=" * 60)

    return vectorizer, X_train, X_test, train_labels, test_labels


if __name__ == "__main__":
    fit_and_transform_tfidf()