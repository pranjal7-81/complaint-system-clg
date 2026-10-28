import sqlite3
import os
from datetime import datetime, timedelta
import random

from database import create_database
from src.predict import predict_complaint
from src.hive_analytics import sync_hive_warehouse
from src.powerbi_export import export_powerbi_star_schema

DB_NAME = "complaints.db"

sample_complaints = [
    {
        "customer": "user",
        "text": "Equifax is reporting a delinquent collection account of $1,450 from an unknown medical provider that does not belong to me. I suspect identity theft and disputed this 45 days ago with no response.",
        "status": "In Progress",
        "admin_notes": "Formal FCRA 30-day investigation notice issued to Credit Reporting Bureau. Flagged for immediate compliance triage."
    },
    {
        "customer": "user",
        "text": "Someone used my credit card without my permission to purchase $850 worth of electronics online and my account was debited immediately.",
        "status": "In Progress",
        "admin_notes": "Card frozen immediately. Provisional credit of $850 credited to cardholder account. Chargeback initiated with acquiring merchant."
    },
    {
        "customer": "user",
        "text": "A third-party debt collector keeps calling my workplace 5 times a day demanding payment for a credit card debt that was already paid off in 2021. They threatened wage garnishment.",
        "status": "Pending",
        "admin_notes": "FDCPA violation investigation initiated. Cease-and-desist communication notice dispatched to collection agency."
    },
    {
        "customer": "user",
        "text": "I made my monthly mortgage payment of $2,100 on time, but the servicer misapplied the funds into escrow instead of principal, and assessed an improper late fee of $120.",
        "status": "Resolved",
        "admin_notes": "Mortgage servicer corrected ledger allocation to principal & interest. Late charge of $120 reversed and credited."
    },
    {
        "customer": "john_doe",
        "text": "I initiated an international wire transfer of $3,500 via SWIFT for urgent family medical expenses 8 days ago. The funds have left my account but never arrived at the beneficiary bank.",
        "status": "Pending",
        "admin_notes": "Wire tracking trace ticket opened with intermediary clearing bank. High-urgency wire recall inquiry pending."
    },
    {
        "customer": "john_doe",
        "text": "My bank charged four consecutive overdraft fees of $35 each on the same day due to an internal system batch processing reordering of debit transactions.",
        "status": "Resolved",
        "admin_notes": "Reviewed transaction posting order. Courtesy refund of $140 credited back to customer checking account."
    },
    {
        "customer": "john_doe",
        "text": "My student loan servicer failed to certify my Public Service Loan Forgiveness (PSLF) payment count despite 120 qualifying on-time payments made over 10 years.",
        "status": "In Progress",
        "admin_notes": "Escalated to Federal Student Aid ombudsman unit for payment history audit and discharge verification."
    },
    {
        "customer": "john_doe",
        "text": "I received a notice threatening repossession of my vehicle even though my monthly auto lease payment of $420 was debited directly via auto-pay on the 1st of this month.",
        "status": "Pending",
        "admin_notes": "URGENT ESCALATION: Auto repossession hold confirmed with recovery operations. Payment trace located and reconciled."
    },
    {
        "customer": "user",
        "text": "My debit card was swallowed by an ATM machine at a local branch during an error and $300 cash was not dispensed but deducted from my balance.",
        "status": "In Progress",
        "admin_notes": "ATM cash cassette count requested from cash-in-transit vendor. Provisional credit of $300 issued."
    },
    {
        "customer": "john_doe",
        "text": "I applied for a credit limit increase on my card 3 weeks ago. Can you explain the status and documentation required for underwriting review?",
        "status": "Resolved",
        "admin_notes": "Provided underwriting status update and secure portal link for submitting updated proof of income."
    }
]


def seed_database(reset: bool = True):
    print("=" * 60)
    print("        DATABASE SEEDING & INITIALIZATION")
    print("=" * 60)
    create_database()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if reset:
        cursor.execute("DELETE FROM complaints")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='complaints'")
        conn.commit()
        print("[+] Existing complaint records cleared for fresh demo.")

    print("\nRunning AI prediction & routing on sample complaints...")
    now = datetime.now()

    for idx, item in enumerate(sample_complaints):
        customer = item["customer"]
        text = item["text"]
        status = item["status"]
        admin_notes = item["admin_notes"]

        analysis = predict_complaint(text)
        category = analysis["category"]
        priority = analysis["priority"]
        department = analysis["department"]
        macro_product = analysis["macro_product"]

        delta_hours = random.randint(2, 120)
        timestamp = (now - timedelta(hours=delta_hours)).strftime("%Y-%m-%d %H:%M")
        update_ts = (now - timedelta(hours=max(1, delta_hours - 4))).strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO complaints (customer_username, complaint, category, macro_product, priority, department, status, admin_notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer, text, category, macro_product, priority, department, status, admin_notes, timestamp, update_ts))

        print(f"  [+] #{idx+1:02d} | User: {customer:<8} | [{priority:<6}] -> {category[:24]:<24} | Status: {status}")

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    conn.close()

    print(f"\n[+] Successfully seeded {count} complaint tickets into SQLite database!")

    sync_hive_warehouse()
    export_powerbi_star_schema()
    print("Database seeding & Big Data warehouse sync complete!\n")


if __name__ == "__main__":
    seed_database(reset=True)
