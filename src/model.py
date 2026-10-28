import json
import os
import pickle
import time
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

TRAIN_PATH = "data/processed/train.csv"
TEST_PATH = "data/processed/test.csv"
MODEL_DIR = "artifacts"

os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_compare_models():
    print("=" * 65)
    print("   MULTI-MODEL MACHINE LEARNING PIPELINE (5 BENCHMARK MODELS)   ")
    print("=" * 65)

    print(f"\n1. Loading processed datasets...")
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    X_train_raw = train_df['text'].fillna('')
    y_train = train_df['category']
    X_test_raw = test_df['text'].fillna('')
    y_test = test_df['category']

    print(f"   - Training records: {len(train_df):,}")
    print(f"   - Testing records : {len(test_df):,}")
    print(f"   - Unique classes  : {y_train.nunique()}")

    print("\n2. Vectorizing text narratives via TF-IDF (5,000 features, 1-2 ngrams)...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english",
        sublinear_tf=True
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    with open(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    # Define 5 models
    models = {
        "Linear Support Vector (SGD)": SGDClassifier(loss='modified_huber', max_iter=500, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=300, random_state=42, solver='lbfgs'),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Random Forest": RandomForestClassifier(n_estimators=60, max_depth=25, random_state=42, n_jobs=-1),
        "Decision Tree": DecisionTreeClassifier(max_depth=25, random_state=42)
    }

    results = []
    trained_models = {}

    print("\n3. Training & Evaluating 5 Machine Learning Models:")
    print("-" * 65)

    for name, clf in models.items():
        t0 = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - t0

        t_inf0 = time.time()
        preds = clf.predict(X_test)
        inf_latency_ms = ((time.time() - t_inf0) / X_test.shape[0]) * 1000

        acc = accuracy_score(y_test, preds)
        prec_macro = precision_score(y_test, preds, average='macro', zero_division=0)
        rec_macro = recall_score(y_test, preds, average='macro', zero_division=0)
        f1_macro = f1_score(y_test, preds, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, preds, average='weighted', zero_division=0)

        trained_models[name] = clf

        metrics = {
            "model_name": name,
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "train_time_sec": round(float(train_time), 2),
            "latency_ms_per_sample": round(float(inf_latency_ms), 3)
        }
        results.append(metrics)
        print(f"[{name:<26}] Acc: {acc*100:5.2f}% | F1: {f1_macro:5.3f} | Latency: {inf_latency_ms:5.2f}ms | Train Time: {train_time:5.2f}s")

    # Save models
    with open(os.path.join(MODEL_DIR, "logistic_regression_model.pkl"), "wb") as f:
        pickle.dump(trained_models["Logistic Regression"], f)

    with open(os.path.join(MODEL_DIR, "naive_bayes_model.pkl"), "wb") as f:
        pickle.dump(trained_models["Multinomial Naive Bayes"], f)

    with open(os.path.join(MODEL_DIR, "random_forest_model.pkl"), "wb") as f:
        pickle.dump(trained_models["Random Forest"], f)

    with open(os.path.join(MODEL_DIR, "linear_svc_model.pkl"), "wb") as f:
        pickle.dump(trained_models["Linear Support Vector (SGD)"], f)

    with open(os.path.join(MODEL_DIR, "decision_tree_model.pkl"), "wb") as f:
        pickle.dump(trained_models["Decision Tree"], f)

    # Save comparison JSON
    with open(os.path.join(MODEL_DIR, "model_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print(f"{'Model':<28} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Macro':<10}")
    print("-" * 65)
    for r in sorted(results, key=lambda x: x['accuracy'], reverse=True):
        print(f"{r['model_name']:<28} | {r['accuracy']*100:7.2f}%  | {r['precision_macro']:<10.4f} | {r['recall_macro']:<10.4f} | {r['f1_macro']:<10.4f}")
    print("=" * 65)

    print(f"\nAll 5 models & performance metrics successfully saved to '{MODEL_DIR}/'!")
    return results


if __name__ == "__main__":
    train_and_compare_models()