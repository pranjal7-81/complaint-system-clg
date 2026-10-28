import csv
import os
import random
from collections import defaultdict, Counter
import pandas as pd
from src.preprocessing import clean_text

RAW_DIR = os.path.join('data', 'raw')
PROCESSED_DIR = os.path.join('data', 'processed')
TRAIN_RAW_PATH = os.path.join(RAW_DIR, 'train.csv')
TEST_RAW_PATH = os.path.join(RAW_DIR, 'test.csv')

CLEANED_DATA_PATH = os.path.join(PROCESSED_DIR, 'cleaned_complaints.csv')
TRAIN_DATA_PATH = os.path.join(PROCESSED_DIR, 'train.csv')
TEST_DATA_PATH = os.path.join(PROCESSED_DIR, 'test.csv')


def normalize_category(cat: str) -> str:
    """Normalize raw CFPB product text into standardized banking categories."""
    if not cat or not isinstance(cat, str):
        return 'Other Financial Services'
    c = cat.strip().lower()
    if 'credit reporting' in c or 'credit repair' in c:
        return 'Credit Reporting & Repair'
    elif 'debt collection' in c:
        return 'Debt Collection'
    elif 'mortgage' in c:
        return 'Mortgages & Home Loans'
    elif 'card' in c:
        return 'Credit & Debit Cards'
    elif 'checking' in c or 'savings' in c or 'bank account' in c:
        return 'Checking & Savings Accounts'
    elif 'student' in c:
        return 'Student Loans'
    elif 'vehicle' in c or 'lease' in c:
        return 'Vehicle Loans & Leasing'
    elif 'payday' in c or 'consumer loan' in c or 'personal loan' in c:
        return 'Consumer & Personal Loans'
    elif 'transfer' in c or 'money service' in c or 'currency' in c:
        return 'Money Transfers & Digital Payments'
    else:
        return 'Other Financial Services'


def get_macro_product(category: str) -> str:
    """Map normalized category to CFPB-style macro financial domain."""
    cat = category.lower()
    if 'card' in cat:
        return 'Card & Payment Services'
    elif 'transfer' in cat or 'digital' in cat:
        return 'Money Transfers & Digital Payments'
    elif 'mortgage' in cat:
        return 'Mortgage & Housing Finance'
    elif 'debt' in cat:
        return 'Debt Collection & Recoveries'
    elif 'credit reporting' in cat or 'repair' in cat:
        return 'Credit Reporting & Dispute Services'
    elif 'student' in cat or 'consumer' in cat or 'vehicle' in cat:
        return 'Consumer & Educational Lending'
    elif 'checking' in cat or 'savings' in cat or 'bank' in cat:
        return 'Banking & Deposit Accounts'
    else:
        return 'General Financial Services'


def get_department(category: str, text: str) -> str:
    """Route complaint to relevant specialized banking/operational department."""
    cat_lower = category.lower()
    text_lower = text.lower()
    
    # Critical Security & Fraud routing
    fraud_flags = ['fraud', 'stolen', 'unauthorized', 'without my permission', 'without permission', 
                   'hacked', 'identity theft', 'scam', 'compromised', 'victim']
    if any(k in text_lower for k in fraud_flags):
        if 'card' in cat_lower or 'card' in text_lower:
            return 'Card Security Team'
        return 'Fraud & Risk Prevention'
    
    # Domain specific operational routing
    if 'credit reporting' in cat_lower or 'credit repair' in cat_lower:
        return 'Credit Dispute Bureau'
    elif 'debt' in cat_lower:
        return 'Debt Collection & Recoveries'
    elif 'mortgage' in cat_lower:
        return 'Mortgage & Lending Services'
    elif 'transfer' in cat_lower or 'digital' in cat_lower:
        return 'Payments & Wire Operations'
    elif 'checking' in cat_lower or 'savings' in cat_lower or 'bank' in cat_lower:
        return 'Billing & Account Operations'
    elif 'card' in cat_lower:
        return 'Card Security Team'
    elif 'loan' in cat_lower:
        return 'Consumer Lending Team'
    else:
        return 'General Customer Support'


def get_priority(category: str, text: str, timely_response: str = 'Yes', company_response: str = '') -> str:
    """
    Assign urgency priority (High, Medium, Low) based on narrative urgency flags,
    regulatory SLA status, and monetary dispute risk.
    """
    text_lower = text.lower()
    cat_lower = category.lower()
    comp_resp_lower = company_response.lower()

    # HIGH Priority (4-hour SLA):
    # 1. Emergency keywords (unauthorized debits, stolen identity, fraud, foreclosure)
    # 2. SLA breach flag (Timely response? == 'No')
    # 3. Monetary restitution required (Closed with monetary relief)
    high_kws = ['stolen', 'fraud', 'unauthorized', 'hacked', 'deducted', 'victim', 'emergency', 
                'compromised', 'identity theft', 'foreclosure', 'eviction', 'repossession']
    
    if (any(k in text_lower for k in high_kws) or 
        timely_response.strip().lower() == 'no' or 
        'monetary relief' in comp_resp_lower):
        return 'High'

    # LOW Priority (72-hour SLA): Routine procedural inquiries, fee inquiries, statements
    low_kws = ['statement', 'inquiry', 'how to', 'general question', 'rewards', 'promotional']
    if any(k in text_lower for k in low_kws) and not any(k in text_lower for k in ['fee', 'charge', 'delay', 'dispute']):
        return 'Low'

    # MEDIUM Priority (24-hour SLA): Standard processing delays, disputes, errors
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


def clean_and_enrich_records(records: list[dict], min_word_count: int = 5) -> list[dict]:
    cleaned = []
    seen = set()
    dropped_empty = 0
    dropped_short = 0
    dropped_dupes = 0

    for r in records:
        text = r.get('Consumer complaint narrative') or r.get('text') or r.get('complaint') or ''
        raw_cat = r.get('Product') or r.get('category') or 'Other Financial Services'
        timely = r.get('Timely response?') or 'Yes'
        comp_resp = r.get('Company response to consumer') or ''
        company = r.get('Company') or 'Financial Institution'
        state = r.get('State') or 'US'
        issue = r.get('Issue') or 'General Grievance'
        complaint_id = r.get('Complaint ID') or ''

        text = text.strip()
        if not text:
            dropped_empty += 1
            continue

        c_text = clean_text(text)
        words = c_text.split()
        if len(words) < min_word_count:
            dropped_short += 1
            continue

        # Prevent exact duplicate texts
        text_signature = " ".join(words[:25])
        if text_signature in seen:
            dropped_dupes += 1
            continue
        seen.add(text_signature)

        cat = normalize_category(raw_cat)
        macro_prod = get_macro_product(cat)
        dept = get_department(cat, text)
        priority = get_priority(cat, text, timely_response=timely, company_response=comp_resp)

        cleaned.append({
            'text': c_text,
            'raw_text': text[:500],  # Keep sample raw text snippet
            'category': cat,
            'macro_product': macro_prod,
            'department': dept,
            'priority': priority,
            'timely_response': timely,
            'company_response': comp_resp,
            'company': company,
            'state': state,
            'issue': issue,
            'complaint_id': complaint_id,
            'word_count': len(words)
        })

    print(f"Cleaning Summary: Initial={len(records):,}, Empty={dropped_empty}, Short={dropped_short}, Dupes={dropped_dupes}, Clean={len(cleaned):,}")
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
    print(f"Saved {len(records):,} records to {file_path}")


def prepare_datasets():
    print("=" * 65)
    print("    CFPB DATASET PREPARATION, ENRICHMENT & ROUTING PIPELINE    ")
    print("=" * 65)
    print(f"Loading raw train data from: {TRAIN_RAW_PATH}")
    raw_train = load_raw_dataset(TRAIN_RAW_PATH)
    print(f"Loading raw test data from : {TEST_RAW_PATH}")
    raw_test = load_raw_dataset(TEST_RAW_PATH)

    print("\nProcessing and enriching training complaints...")
    clean_train = clean_and_enrich_records(raw_train)
    print("\nProcessing and enriching testing complaints...")
    clean_test = clean_and_enrich_records(raw_test)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    save_dataset_csv(clean_train, TRAIN_DATA_PATH)
    save_dataset_csv(clean_test, TEST_DATA_PATH)

    all_cleaned = clean_train + clean_test
    save_dataset_csv(all_cleaned, CLEANED_DATA_PATH)
    print(f"\n[SUCCESS] Dataset preparation complete! Total processed: {len(all_cleaned):,} records.\n")


if __name__ == '__main__':
    prepare_datasets()
