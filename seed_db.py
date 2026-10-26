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
        "text": "Someone used my debit card without my permission at a gas station and $250 was deducted.",
        "status": "In Progress",
        "admin_notes": "Card blocked immediately. Dispatched to Fraud & Risk Prevention for transaction chargeback recovery."
    },
    {
        "customer": "user",
        "text": "My credit card was stolen from my wallet yesterday and I need to freeze it immediately to prevent fraud.",
        "status": "In Progress",
        "admin_notes": "Card frozen. Emergency replacement card requested via express delivery."
    },
    {
        "customer": "user",
        "text": "I requested a replacement contactless card 12 days ago but I still have not received it in the mail.",
        "status": "Pending",
        "admin_notes": "Ticket queued. Postal dispatch tracking number requested from Card Fulfillment team."
    },
    {
        "customer": "user",
        "text": "I noticed an unknown recurring monthly account maintenance fee of $25 on my checking account statement.",
        "status": "Resolved",
        "admin_notes": "Waived the $25 maintenance fee and credited back to account. Upgraded account tier to zero-fee student tier."
    },
    {
        "customer": "john_doe",
        "text": "I tried to transfer money to another account via SEPA but the transfer is stuck in pending status since yesterday.",
        "status": "Pending",
        "admin_notes": "Pending clearing batch check with European Central Clearing House."
    },
    {
        "customer": "john_doe",
        "text": "An unauthorized ATM cash withdrawal of $400 appeared on my account history while I was out of town.",
        "status": "In Progress",
        "admin_notes": "Security video requested from ATM operator. Provisional $400 credit issued."
    },
    {
        "customer": "john_doe",
        "text": "I cannot log in to my mobile banking app because I forgot my passcode and verification SMS is not arriving.",
        "status": "Resolved",
        "admin_notes": "Identity verified via telephone KYC. Passcode reset link sent securely to customer's verified email."
    },
    {
        "customer": "john_doe",
        "text": "Why was I charged an international transaction exchange fee when purchasing online from a local merchant?",
        "status": "Resolved",
        "admin_notes": "Merchant processor is registered in the UK. Explained international interchange fee regulations."
    },
    {
        "customer": "user",
        "text": "My virtual card was declined when trying to pay for a software subscription online.",
        "status": "Pending",
        "admin_notes": "3D Secure authentication failure investigated. Recommended refreshing disposable virtual card."
    },
    {
        "customer": "user",
        "text": "I deposited a paycheck of $1,200 at the branch ATM two days ago but my account balance has not updated.",
        "status": "In Progress",
        "admin_notes": "Cheque clearance underway. Funds expected to settle by end of business day."
    },
    {
        "customer": "john_doe",
        "text": "I need to dispute a double charge of $89.99 for groceries at supermarket yesterday.",
        "status": "In Progress",
        "admin_notes": "Merchant reconciliation request submitted for the duplicate debit."
    },
    {
        "customer": "john_doe",
        "text": "Can you explain the age limit and identity documentation required to open a joint savings account?",
        "status": "Resolved",
        "admin_notes": "Guidelines and digital KYC requirements emailed to customer."
    },
    {
        "customer": "user",
        "text": "My transfer to a beneficiary was rejected without any explanation and funds were not credited back.",
        "status": "Pending",
        "admin_notes": "Beneficiary IBAN format validation issue detected. Reverse transfer initiated."
    },
    {
        "customer": "john_doe",
        "text": "I received an alert that my online banking password was changed from an unrecognized IP address in another country.",
        "status": "Pending",
        "admin_notes": "CRITICAL ESCALATION: User session invalidated, web banking locked pending two-factor re-verification."
    },
    {
        "customer": "user",
        "text": "I was promised a refund from an airline 3 weeks ago but it is not showing up in my pending transactions.",
        "status": "Resolved",
        "admin_notes": "Merchant acquirer initiated refund today. Credit settled in user account."
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
