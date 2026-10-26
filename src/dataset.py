import csv
import os
import random
from collections import defaultdict, Counter
from src.preprocessing import clean_text

RAW_DIR = os.path.join('data', 'raw')
PROCESSED_DIR = os.path.join('data', 'processed')
TRAIN_RAW_PATH = os.path.join(RAW_DIR, 'train.csv')
TEST_RAW_PATH = os.path.join(RAW_DIR, 'test.csv')

CLEANED_DATA_PATH = os.path.join(PROCESSED_DIR, 'cleaned_complaints.csv')
TRAIN_DATA_PATH = os.path.join(PROCESSED_DIR, 'train.csv')
TEST_DATA_PATH = os.path.join(PROCESSED_DIR, 'test.csv')


def get_macro_product(category: str) -> str:
    """Map fine-grained category to CFPB-style macro product domain."""
    cat = category.lower()
    if any(k in cat for k in ['card', 'disposable', 'pin']):
        return 'Credit & Debit Cards'
    elif any(k in cat for k in ['transfer', 'payment', 'exchange', 'wire', 'top_up', 'beneficiary']):
        return 'Money Transfers & Payments'
    elif any(k in cat for k in ['atm', 'cash', 'cheque', 'deposit']):
        return 'ATM & Cash Services'
    elif any(k in cat for k in ['fee', 'charge', 'refund', 'balance']):
        return 'Account Billing & Fees'
    elif any(k in cat for k in ['passcode', 'verify', 'identity', 'age', 'country']):
        return 'Identity & Security Verification'
    else:
        return 'General Checking & Savings'


def get_department(category: str, text: str) -> str:
    """Route complaint to relevant banking department."""
    cat_lower = category.lower()
    text_lower = text.lower()
    if 'card' in cat_lower and ('stolen' in text_lower or 'lost' in text_lower):
        return 'Card Security Team'
    elif any(k in cat_lower for k in ['not_recognised', 'fraud', 'compromised']) or any(k in text_lower for k in ['fraud', 'stolen', 'unauthorized', 'hacked']):
        return 'Fraud & Risk Prevention'
    elif any(k in cat_lower for k in ['transfer', 'payment', 'top_up', 'beneficiary']):
        return 'Payments & Transfers'
    elif any(k in cat_lower for k in ['charge', 'fee', 'refund', 'balance']):
        return 'Billing & Accounts'
    elif any(k in cat_lower for k in ['passcode', 'login', 'app', 'verify']):
        return 'Customer Tech Support'
    else:
        return 'General Customer Support'


def get_priority(category: str, text: str) -> str:
    """Assign urgency priority (High, Medium, Low)."""
    text_lower = text.lower()
    cat_lower = category.lower()
    high_kws = ['stolen', 'fraud', 'unauthorized', 'hacked', 'deducted', 'victim', 'emergency', 'compromised']
    high_cats = ['lost_or_stolen_card', 'card_payment_not_recognised', 'cash_withdrawal_not_recognised']
    if any(k in text_lower for k in high_kws) or any(c in cat_lower for c in high_cats):
        return 'High'
    low_kws = ['pin', 'passcode', 'password', 'statement', 'virtual card', 'inquiry', 'how to']
    low_cats = ['passcode_forgotten', 'get_disposable_virtual_card', 'card_arrival']
    if any(k in text_lower for k in low_kws) or any(c in cat_lower for c in low_cats):
        return 'Low'
    return 'Medium'


def load_raw_dataset(file_path: str) -> list[dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw dataset file not found at {file_path}")
    records = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def clean_and_enrich_records(records: list[dict], min_word_count: int = 3) -> list[dict]:
    cleaned = []
    seen = set()
    dropped_empty = 0
    dropped_short = 0
    dropped_dupes = 0

    for r in records:
        text = r.get('text') or r.get('Consumer complaint narrative') or r.get('complaint') or ''
        cat = r.get('category') or r.get('Product') or 'general_inquiry'
        text = text.strip()
        cat = cat.strip()

        if not text:
            dropped_empty += 1
            continue

        c_text = clean_text(text)
        words = c_text.split()
        if len(words) < min_word_count:
            dropped_short += 1
            continue

        if c_text in seen:
            dropped_dupes += 1
            continue
        seen.add(c_text)

        macro_prod = get_macro_product(cat)
        dept = get_department(cat, text)
        priority = get_priority(cat, text)

        cleaned.append({
            'text': c_text,
            'raw_text': text,
            'category': cat,
            'macro_product': macro_prod,
            'department': dept,
            'priority': priority,
            'word_count': len(words)
        })

    print(f"Cleaning Summary: Initial={len(records)}, Empty={dropped_empty}, Short={dropped_short}, Dupes={dropped_dupes}, Clean={len(cleaned)}")
    return cleaned


def save_dataset_csv(records: list[dict], file_path: str):
    if not records:
        return
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {file_path}")


def prepare_datasets():
    print("=" * 60)
    print("       DATASET PREPARATION & ENRICHMENT PIPELINE")
    print("=" * 60)
    raw_train = load_raw_dataset(TRAIN_RAW_PATH)
    raw_test = load_raw_dataset(TEST_RAW_PATH)

    clean_train = clean_and_enrich_records(raw_train)
    clean_test = clean_and_enrich_records(raw_test)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    save_dataset_csv(clean_train, TRAIN_DATA_PATH)
    save_dataset_csv(clean_test, TEST_DATA_PATH)

    all_cleaned = clean_train + clean_test
    save_dataset_csv(all_cleaned, CLEANED_DATA_PATH)
    print("Dataset preparation complete!\n")


if __name__ == '__main__':
    prepare_datasets()
