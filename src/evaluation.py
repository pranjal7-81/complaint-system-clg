import json
import os
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

TEST_PATH = "data/processed/test.csv"
ARTIFACTS_DIR = "artifacts"


def run_comprehensive_evaluation():
    print("=" * 65)
    print("     MODEL EVALUATION & VISUALIZATION GENERATOR     ")
    print("=" * 65)

    test_df = pd.read_csv(TEST_PATH)
    X_test_raw = test_df['text'].fillna('')
    y_test = test_df['category']

    with open(os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    X_test = vectorizer.transform(X_test_raw)

    with open(os.path.join(ARTIFACTS_DIR, "model_comparison.json"), "r") as f:
        comparison_results = json.load(f)

    print("\n1. Generating Model Performance Comparison Bar Chart...")
    model_names = [m["model_name"] for m in comparison_results]
    accuracies = [m["accuracy"] * 100 for m in comparison_results]
    f1_scores = [m["f1_macro"] * 100 for m in comparison_results]

    x = np.arange(len(model_names))
    width = 0.35

    plt.figure(figsize=(10, 5.5))
    plt.bar(x - width/2, accuracies, width, label='Accuracy (%)', color='#2563eb')
    plt.bar(x + width/2, f1_scores, width, label='F1-Score Macro (%)', color='#059669')

    plt.xlabel('Machine Learning Model', fontweight='bold', fontsize=11)
    plt.ylabel('Score (%)', fontweight='bold', fontsize=11)
    plt.title('Performance Comparison Across 5 Machine Learning Models', fontsize=13, fontweight='bold', pad=15)
    plt.xticks(x, model_names, rotation=15, ha='right', fontsize=9.5)
    plt.ylim(0, 105)
    plt.legend(frameon=True, loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    chart_path = os.path.join(ARTIFACTS_DIR, "model_comparison_chart.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"   [+] Saved comparison chart: {chart_path}")

    # 2. Confusion matrix for top 8 high-volume categories
    print("\n2. Generating Confusion Matrix Heatmap for Primary Banking Intents...")
    with open(os.path.join(ARTIFACTS_DIR, "logistic_regression_model.pkl"), "rb") as f:
        lr_model = pickle.load(f)

    preds = lr_model.predict(X_test)
    top_categories = y_test.value_counts().head(8).index.tolist()

    # Filter to top categories for readable confusion matrix
    preds_series = pd.Series(preds, index=y_test.index)
    mask = y_test.isin(top_categories) & preds_series.isin(top_categories)
    y_test_filtered = y_test[mask]
    preds_filtered = preds_series[mask]

    cm = confusion_matrix(y_test_filtered, preds_filtered, labels=top_categories)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(9, 7))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=[c.replace('_', ' ')[:18] for c in top_categories],
                yticklabels=[c.replace('_', ' ')[:18] for c in top_categories])
    plt.title('Normalized Confusion Matrix (Top Primary Banking Categories)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Predicted Intent', fontweight='bold')
    plt.ylabel('True Intent', fontweight='bold')
    plt.xticks(rotation=30, ha='right', fontsize=8.5)
    plt.yticks(rotation=0, fontsize=8.5)
    plt.tight_layout()

    cm_path = os.path.join(ARTIFACTS_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"   [+] Saved confusion matrix heatmap: {cm_path}")

    print("\n" + "=" * 65)
    print("Model Evaluation & Visualizations completed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    run_comprehensive_evaluation()
