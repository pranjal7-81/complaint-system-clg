import sqlite3
from datetime import datetime

DB_NAME = "complaints.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Users Table for Authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
    """)

    # 2. Complaints Table with Customer Ownership & Tracking Notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_username TEXT NOT NULL,
            complaint TEXT NOT NULL,
            category TEXT NOT NULL,
            macro_product TEXT DEFAULT 'General Banking',
            priority TEXT DEFAULT 'Medium',
            department TEXT DEFAULT 'General Customer Support',
            status TEXT DEFAULT 'Pending',
            admin_notes TEXT DEFAULT 'Complaint registered and assigned to support team for initial review.',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Migrations for existing schemas
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [row[1] for row in cursor.fetchall()]

    if "customer_username" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN customer_username TEXT DEFAULT 'user'")
    if "macro_product" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN macro_product TEXT DEFAULT 'General Banking'")
    if "priority" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN priority TEXT DEFAULT 'Medium'")
    if "department" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN department TEXT DEFAULT 'General Customer Support'")
    if "status" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN status TEXT DEFAULT 'Pending'")
    if "admin_notes" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN admin_notes TEXT DEFAULT 'Complaint registered and under review.'")
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN created_at TEXT")
    if "updated_at" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN updated_at TEXT")

    # Seed default user accounts if not present
    default_users = [
        ("admin", "admin123", "Chief Operations Admin", "admin"),
        ("user", "user123", "Tanmay Awal", "customer"),
        ("john_doe", "pass123", "Johnathan Doe", "customer")
    ]
    for u, p, name, r in default_users:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        """, (u, p, name, r))

    conn.commit()
    conn.close()


def authenticate_user(username: str, password: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, full_name, role
        FROM users
        WHERE username = ? AND password = ?
    """, (username.strip(), password.strip()))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"username": user[0], "full_name": user[1], "role": user[2]}
    return None


def register_user(username: str, password: str, full_name: str, role: str = "customer"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        """, (username.strip(), password.strip(), full_name.strip(), role))
        conn.commit()
        success = True
        msg = "Account registered successfully! You can now log in."
    except sqlite3.IntegrityError:
        success = False
        msg = f"Username '{username}' already exists. Please pick another."
    conn.close()
    return success, msg


def add_complaint(
    customer_username: str,
    complaint: str,
    category: str,
    macro_product: str = "General Banking",
    priority: str = "Medium",
    department: str = "General Customer Support",
    status: str = "Pending",
    admin_notes: str = "Complaint registered and queued for investigation."
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
        INSERT INTO complaints (customer_username, complaint, category, macro_product, priority, department, status, admin_notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_username, complaint, category, macro_product, priority, department, status, admin_notes, now_str, now_str))

    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return complaint_id


def get_customer_complaints(customer_username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, complaint, category, macro_product, priority, department, status, admin_notes, created_at, updated_at
        FROM complaints
        WHERE customer_username = ?
        ORDER BY id DESC
    """, (customer_username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_complaints(status_filter: str = None, priority_filter: str = None, department_filter: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT id, customer_username, complaint, category, macro_product, priority, department, status, admin_notes, created_at, updated_at
        FROM complaints
        WHERE 1=1
    """
    params = []

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)
    if department_filter and department_filter != "All":
        query += " AND department = ?"
        params.append(department_filter)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_complaint_status_and_notes(complaint_id: int, new_status: str, admin_notes: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if admin_notes:
        cursor.execute("""
            UPDATE complaints
            SET status = ?, admin_notes = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, admin_notes, now_str, complaint_id))
    else:
        cursor.execute("""
            UPDATE complaints
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now_str, complaint_id))

    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'High'")
    high_priority = cursor.fetchone()[0]

    cursor.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category ORDER BY COUNT(*) DESC LIMIT 6")
    top_categories = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT department, COUNT(*) FROM complaints GROUP BY department ORDER BY COUNT(*) DESC")
    dept_breakdown = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT priority, COUNT(*) FROM complaints GROUP BY priority")
    prio_breakdown = {r[0]: r[1] for r in cursor.fetchall()}

    conn.close()
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_priority": high_priority,
        "top_categories": top_categories,
        "department_breakdown": dept_breakdown,
        "priority_breakdown": prio_breakdown
    }


if __name__ == "__main__":
    create_database()
    print("Database and User tables successfully initialized.")