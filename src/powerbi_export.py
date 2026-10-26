import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "complaints.db"
POWERBI_DIR = os.path.join("data", "powerbi")
os.makedirs(POWERBI_DIR, exist_ok=True)


def export_powerbi_star_schema():
    print("=" * 60)
    print("      POWER BI / BUSINESS INTELLIGENCE DATA EXPORTER")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM complaints", conn)
    except Exception as e:
        print(f"Error reading from database: {e}")
        conn.close()
        return
    conn.close()

    if df.empty:
        print("Warning: Complaints database is empty. Please seed or submit complaints first.")
        return

    # Ensure required columns
    if 'priority' not in df.columns:
        df['priority'] = 'Medium'
    if 'department' not in df.columns:
        df['department'] = 'General Customer Support'
    if 'created_at' not in df.columns:
        df['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Convert / Parse dates
    df['created_date'] = pd.to_datetime(df['created_at'], errors='coerce').dt.date
    df['created_date'] = df['created_date'].fillna(datetime.now().date())

    # 1. Dimension: dim_category
    unique_categories = df['category'].unique()
    dim_category = pd.DataFrame({
        'category_id': range(1, len(unique_categories) + 1),
        'category_name': unique_categories,
        'category_clean': [c.replace('_', ' ').title() for c in unique_categories]
    })
    cat_path = os.path.join(POWERBI_DIR, "dim_category.csv")
    dim_category.to_csv(cat_path, index=False)
    print(f"[+] Exported Dimension: {cat_path} ({len(dim_category)} records)")

    # 2. Dimension: dim_department
    unique_depts = df['department'].unique()
    dim_dept = pd.DataFrame({
        'department_id': range(1, len(unique_depts) + 1),
        'department_name': unique_depts
    })
    dept_path = os.path.join(POWERBI_DIR, "dim_department.csv")
    dim_dept.to_csv(dept_path, index=False)
    print(f"[+] Exported Dimension: {dept_path} ({len(dim_dept)} records)")

    # 3. Dimension: dim_priority
    dim_priority = pd.DataFrame({
        'priority_id': [1, 2, 3],
        'priority_level': ['High', 'Medium', 'Low'],
        'sla_hours': [4, 24, 72]
    })
    prio_path = os.path.join(POWERBI_DIR, "dim_priority.csv")
    dim_priority.to_csv(prio_path, index=False)
    print(f"[+] Exported Dimension: {prio_path} ({len(dim_priority)} records)")

    # 4. Fact Table: fact_complaints
    df_fact = df.copy()
    cat_map = dict(zip(dim_category['category_name'], dim_category['category_id']))
    dept_map = dict(zip(dim_dept['department_name'], dim_dept['department_id']))
    prio_map = dict(zip(dim_priority['priority_level'], dim_priority['priority_id']))

    df_fact['category_id'] = df_fact['category'].map(cat_map)
    df_fact['department_id'] = df_fact['department'].map(dept_map)
    df_fact['priority_id'] = df_fact['priority'].map(prio_map)
    df_fact['is_resolved'] = (df_fact['status'] == 'Resolved').astype(int)
    df_fact['is_pending'] = (df_fact['status'] == 'Pending').astype(int)
    df_fact['is_in_progress'] = (df_fact['status'] == 'In Progress').astype(int)
    df_fact['is_high_risk'] = (df_fact['priority'] == 'High').astype(int)

    fact_path = os.path.join(POWERBI_DIR, "fact_complaints.csv")
    df_fact.to_csv(fact_path, index=False)
    print(f"[+] Exported Fact Table: {fact_path} ({len(df_fact)} records)")

    # 5. KPI Summary for quick BI scorecard
    total = len(df)
    resolved = int(df['status'].eq('Resolved').sum())
    pending = int(df['status'].eq('Pending').sum())
    in_prog = int(df['status'].eq('In Progress').sum())
    high_prio = int(df['priority'].eq('High').sum())

    kpi_df = pd.DataFrame([{
        "Metric": "Total Complaints Ingested", "Value": total
    }, {
        "Metric": "Resolution Rate (%)", "Value": round((resolved / total) * 100, 1) if total else 0
    }, {
        "Metric": "High Urgency Escalation (%)", "Value": round((high_prio / total) * 100, 1) if total else 0
    }, {
        "Metric": "Pending Backlog", "Value": pending
    }, {
        "Metric": "Active In-Progress Tickets", "Value": in_prog
    }])
    kpi_path = os.path.join(POWERBI_DIR, "kpi_summary.csv")
    kpi_df.to_csv(kpi_path, index=False)
    print(f"[+] Exported KPI Summary: {kpi_path}")
    print("=" * 60)
    print("Power BI Star Schema export successfully finished!")
    print("=" * 60)


if __name__ == "__main__":
    export_powerbi_star_schema()
