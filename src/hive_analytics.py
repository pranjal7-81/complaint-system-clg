import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "complaints.db"
WAREHOUSE_DIR = os.path.join("warehouse", "tablespace", "external", "hive")
os.makedirs(WAREHOUSE_DIR, exist_ok=True)


def sync_hive_warehouse():
    """Sync complaints database to simulated Hive / HDFS warehouse storage layout."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM complaints", conn)
    except Exception as e:
        print(f"Error reading DB: {e}")
        conn.close()
        return None
    conn.close()

    if df.empty:
        return None

    # Write simulated HDFS partitioned files: status={status}/priority={priority}/part-00000.csv
    for (status, priority), sub_df in df.groupby(['status', 'priority']):
        part_dir = os.path.join(WAREHOUSE_DIR, f"status={status}", f"priority={priority}")
        os.makedirs(part_dir, exist_ok=True)
        sub_df.to_csv(os.path.join(part_dir, "part-00000.csv"), index=False)

    # Master table for Hive SQL querying
    master_path = os.path.join(WAREHOUSE_DIR, "complaints_master.csv")
    df.to_csv(master_path, index=False)
    return df


def execute_hive_query(query_type: str = "department_kpis") -> pd.DataFrame:
    """Execute analytical HiveQL queries over the complaint warehouse."""
    conn = sqlite3.connect(DB_PATH)

    if query_type == "department_kpis":
        # Analytical aggregation with percentage share
        sql = """
            SELECT 
                department,
                COUNT(*) AS total_complaints,
                SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) AS high_priority_count,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
                ROUND(SUM(CASE WHEN status = 'Resolved' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 1) AS resolution_rate_pct
            FROM complaints
            GROUP BY department
            ORDER BY total_complaints DESC
        """
    elif query_type == "high_risk_backlog":
        # High urgency unresolved complaints
        sql = """
            SELECT 
                id, 
                category, 
                department, 
                priority, 
                status, 
                created_at,
                complaint
            FROM complaints
            WHERE priority = 'High' AND status != 'Resolved'
            ORDER BY id DESC
        """
    elif query_type == "category_volume_pareto":
        # Category volume ranking
        sql = """
            SELECT 
                category,
                COUNT(*) AS complaint_volume,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM complaints), 2) AS share_pct
            FROM complaints
            GROUP BY category
            ORDER BY complaint_volume DESC
            LIMIT 10
        """
    else:
        sql = "SELECT id, complaint, category, priority, department, status, created_at FROM complaints ORDER BY id DESC LIMIT 50"

    result_df = pd.read_sql_query(sql, conn)
    conn.close()
    return result_df


def run_hive_analytics_cli():
    print("=" * 65)
    print("       APACHE HIVE / HADOOP DATA WAREHOUSE QUERY ENGINE       ")
    print("=" * 65)
    sync_hive_warehouse()

    print("\n[HIVE QUERY 1: Department Workload & Resolution SLA Breakdown]")
    df_dept = execute_hive_query("department_kpis")
    print(df_dept.to_string(index=False))

    print("\n[HIVE QUERY 2: Top Unresolved High-Risk Fraud / Stolen Incidents]")
    df_fraud = execute_hive_query("high_risk_backlog")
    print(df_fraud[['id', 'category', 'department', 'priority', 'status']].to_string(index=False))

    print("\n[HIVE QUERY 3: Category Pareto Distribution]")
    df_pareto = execute_hive_query("category_volume_pareto")
    print(df_pareto.to_string(index=False))
    print("\n" + "=" * 65)


if __name__ == "__main__":
    run_hive_analytics_cli()
