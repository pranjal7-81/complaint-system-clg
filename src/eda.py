import csv
import math
import os
from collections import Counter

CLEANED_DATA_PATH = os.path.join('data', 'processed', 'cleaned_complaints.csv')
TRAIN_DATA_PATH = os.path.join('data', 'processed', 'train.csv')
TEST_DATA_PATH = os.path.join('data', 'processed', 'test.csv')


def load_csv_records(file_path: str) -> list[dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def calculate_stats(values: list[int | float]) -> dict:
    if not values:
        return {'min': 0, 'max': 0, 'mean': 0, 'median': 0, 'std': 0}
    s_values = sorted(values)
    n = len(s_values)
    mean_val = sum(s_values) / n
    if n % 2 == 1:
        median_val = s_values[n // 2]
    else:
        median_val = (s_values[n // 2 - 1] + s_values[n // 2]) / 2.0
    variance = sum((x - mean_val) ** 2 for x in s_values) / n
    std_val = math.sqrt(variance)
    return {
        'min': min(s_values),
        'max': max(s_values),
        'mean': round(mean_val, 2),
        'median': round(median_val, 2),
        'std': round(std_val, 2)
    }


def get_ngrams(text: str, n: int = 1) -> list[str]:
    words = text.split()
    if len(words) < n:
        return []
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


def run_eda_report():
    print("=" * 65)
    print("      CUSTOMER COMPLAINT INTELLIGENCE SYSTEM - EDA REPORT     ")
    print("=" * 65)

    cleaned_records = load_csv_records(CLEANED_DATA_PATH)
    train_records = load_csv_records(TRAIN_DATA_PATH)
    test_records = load_csv_records(TEST_DATA_PATH)

    print(f"\n1. DATASET OVERVIEW:")
    print(f"   - Cleaned Dataset Total Records : {len(cleaned_records):,}")
    print(f"   - Training Dataset Samples      : {len(train_records):,}")
    print(f"   - Testing Dataset Samples       : {len(test_records):,}")

    # Macro Product distribution
    print(f"\n2. MACRO FINANCIAL DOMAIN DISTRIBUTION:")
    macro_counts = Counter(r.get('macro_product', 'Other') for r in cleaned_records)
    for m, c in macro_counts.most_common():
        pct = (c / len(cleaned_records)) * 100
        print(f"   - {m:<32}: {c:5d} ({pct:5.1f}%)")

    # Priority distribution
    print(f"\n3. COMPLAINT URGENCY / PRIORITY BREAKDOWN:")
    priority_counts = Counter(r.get('priority', 'Medium') for r in cleaned_records)
    for p, c in priority_counts.most_common():
        pct = (c / len(cleaned_records)) * 100
        print(f"   - {p:<10}: {c:5d} ({pct:5.1f}%)")

    # Department distribution
    print(f"\n4. AUTOMATED DEPARTMENT ROUTING BREAKDOWN:")
    dept_counts = Counter(r.get('department', 'General') for r in cleaned_records)
    for d, c in dept_counts.most_common():
        pct = (c / len(cleaned_records)) * 100
        print(f"   - {d:<26}: {c:5d} ({pct:5.1f}%)")

    # Text length stats
    word_counts = [int(r['word_count']) for r in cleaned_records if r.get('word_count')]
    stats = calculate_stats(word_counts)
    print(f"\n5. COMPLAINT NARRATIVE LENGTH STATISTICS (Word Count):")
    print(f"   - Minimum words  : {stats['min']}")
    print(f"   - Maximum words  : {stats['max']}")
    print(f"   - Mean length    : {stats['mean']}")
    print(f"   - Median length  : {stats['median']}")
    print(f"   - Std deviation  : {stats['std']}")

    # Common unigrams and bigrams
    unigrams = Counter()
    bigrams = Counter()
    stopwords = {'i', 'me', 'my', 'the', 'and', 'to', 'a', 'of', 'in', 'is', 'it', 'for', 'was', 'on', 'with', 'that', 'at', 'have', 'be', 'this', 'from'}
    for r in cleaned_records:
        tokens = [w for w in r['text'].split() if w not in stopwords and len(w) > 2]
        unigrams.update(tokens)
        bigrams.update([" ".join(tokens[i:i+2]) for i in range(len(tokens)-1)])

    print(f"\n6. TOP 10 INFORMATIVE TERMS (UNIGRAMS):")
    for word, freq in unigrams.most_common(10):
        print(f"   - {word:<18} : {freq:,} occurrences")

    print(f"\n7. TOP 10 FREQUENT COMPLAINT BI-GRAMS:")
    for bg, freq in bigrams.most_common(10):
        print(f"   - {bg:<24} : {freq:,} occurrences")

    print("\n" + "=" * 65)


if __name__ == '__main__':
    run_eda_report()
