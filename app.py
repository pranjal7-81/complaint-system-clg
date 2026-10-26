import os
import sqlite3
import json
import pandas as pd
import streamlit as st
from datetime import datetime

from database import (
    create_database,
    authenticate_user,
    register_user,
    add_complaint,
    get_customer_complaints,
    get_all_complaints,
    update_complaint_status_and_notes,
    get_stats
)
from src.predict import predict_complaint
from src.hive_analytics import execute_hive_query, sync_hive_warehouse
from src.powerbi_export import export_powerbi_star_schema
from seed_db import seed_database

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Complaint Intelligence & Big Data Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Database Schema
create_database()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None
if "role" not in st.session_state:
    st.session_state.role = None

# Custom CSS for Sleek, Clutter-Free UI
st.markdown("""
<style>
    /* Global Clean Font & Margins */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0f172a;
        color: white;
        padding: 14px 24px;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    .user-badge {
        background: #1e293b;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        border: 1px solid #334155;
    }
    /* Ticket Cards */
    .ticket-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .priority-badge-high {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .priority-badge-medium {
        background-color: #fef3c7;
        color: #b45309;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .priority-badge-low {
        background-color: #ecfdf5;
        color: #047857;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .status-badge-pending {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge-progress {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge-resolved {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .login-container {
        max-width: 460px;
        margin: 2rem auto;
        padding: 30px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: STRICT LOGIN & REGISTRATION SCREEN (WHEN NOT LOGGED IN)
# ==============================================================================
if not st.session_state.logged_in:
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-bottom: 4px;'>🛡️ Complaint Intelligence Platform</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.95rem; margin-bottom: 24px;'>Please authenticate to access your portal</p>", unsafe_allow_html=True)

        tab_cust, tab_adm, tab_reg = st.tabs(["👤 Customer Login", "🏢 Admin Login", "📝 New Registration"])

        # Customer Login
        with tab_cust:
            with st.form("cust_login_form"):
                c_user = st.text_input("Username", value="user", placeholder="Enter customer username")
                c_pass = st.text_input("Password", type="password", value="user123", placeholder="Enter password")
                c_submit = st.form_submit_button("Log In as Customer", type="primary", use_container_width=True)

                if c_submit:
                    user_data = authenticate_user(c_user, c_pass)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.username = user_data["username"]
                        st.session_state.full_name = user_data["full_name"]
                        st.session_state.role = user_data["role"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            st.caption("💡 Customer Demo: `user` / `user123` or `john_doe` / `pass123`")

        # Admin Login
        with tab_adm:
            with st.form("admin_login_form"):
                a_user = st.text_input("Admin Username", value="admin")
                a_pass = st.text_input("Admin Password", type="password", value="admin123")
                a_submit = st.form_submit_button("Log In as Administrator", type="primary", use_container_width=True)

                if a_submit:
                    user_data = authenticate_user(a_user, a_pass)
                    if user_data and user_data["role"] == "admin":
                        st.session_state.logged_in = True
                        st.session_state.username = user_data["username"]
                        st.session_state.full_name = user_data["full_name"]
                        st.session_state.role = "admin"
                        st.rerun()
                    else:
                        st.error("Invalid administrator credentials.")
            st.caption("💡 Admin Demo: `admin` / `admin123`")

        # New Registration
        with tab_reg:
            with st.form("register_form"):
                r_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan")
                r_user = st.text_input("Choose Username", placeholder="e.g. alex_m")
                r_pass = st.text_input("Choose Password", type="password")
                r_submit = st.form_submit_button("Create Account", use_container_width=True)

                if r_submit:
                    if r_name.strip() and r_user.strip() and r_pass.strip():
                        ok, msg = register_user(r_user, r_pass, r_name, role="customer")
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("All fields are required.")

    st.stop()


# ==============================================================================
# LOGGED IN HEADER BAR (SHARED)
# ==============================================================================
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    role_title = "Customer Portal" if st.session_state.role == "customer" else "Operations & Big Data Command Center"
    st.markdown(f"### 🛡️ Complaint Intelligence • <span style='color: #2563eb;'>{role_title}</span>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<p style='text-align: right; margin-top: 6px;'>👤 <b>{st.session_state.full_name}</b> (<code>{st.session_state.username}</code>)</p>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.role = None
        st.rerun()

st.markdown("---")


# ==============================================================================
# VIEW 2: CUSTOMER ROLE (ONLY RAISE & TRACK COMPLAINTS)
# ==============================================================================
if st.session_state.role == "customer":
    cust_tab1, cust_tab2 = st.tabs(["➕ Raise a New Complaint", "🔍 Track My Complaints"])

    # --- TAB 1: RAISE COMPLAINT ---
    with cust_tab1:
        st.subheader("Submit Your Complaint")
        st.write("Enter your issue below. Our AI model will automatically determine intent, urgency, and route to the correct team.")

        presets = [
            "Quick Scenario Presets (Click to autofill)...",
            "Someone used my debit card without my permission at a gas station and $250 was deducted.",
            "My debit card was swallowed by the ATM machine and no cash was dispensed.",
            "I requested a replacement contactless card two weeks ago but it has not arrived yet.",
            "Why was an extra monthly maintenance charge of $15 debited from my checking account?",
            "I forgot my mobile banking passcode and cannot log in to transfer funds."
        ]
        chosen_preset = st.selectbox("Sample scenarios:", presets, label_visibility="collapsed")
        initial_val = "" if chosen_preset == presets[0] else chosen_preset

        complaint_input = st.text_area(
            "Complaint Narrative:",
            value=initial_val,
            height=140,
            placeholder="Please detail what happened (e.g., unauthorized charge, transfer delay, card delivery)..."
        )

        if st.button("🚀 Submit Complaint Ticket", type="primary"):
            if complaint_input.strip():
                with st.spinner("AI analyzing complaint narrative..."):
                    pred = predict_complaint(complaint_input.strip())
                    new_id = add_complaint(
                        customer_username=st.session_state.username,
                        complaint=complaint_input.strip(),
                        category=pred["category"],
                        macro_product=pred["macro_product"],
                        priority=pred["priority"],
                        department=pred["department"],
                        status="Pending",
                        admin_notes="Ticket registered in automated queue. Assigned to specialized team for initial triage."
                    )
                    sync_hive_warehouse()
                    export_powerbi_star_schema()

                st.success(f"🎉 Complaint successfully registered as **Ticket #{new_id:03d}**!")

                prio_style = f"priority-badge-{pred['priority'].lower()}"
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb; border-radius: 8px; padding: 18px; margin-top: 10px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e3a8a;">📋 Registration Summary</h4>
                    <p style="margin: 4px 0;"><b>Ticket Reference:</b> <code>#{new_id:03d}</code></p>
                    <p style="margin: 4px 0;"><b>Detected Category:</b> <code>{pred['category']}</code></p>
                    <p style="margin: 4px 0;"><b>Financial Domain:</b> {pred['macro_product']}</p>
                    <p style="margin: 4px 0;"><b>Urgency Level:</b> <span class="{prio_style}">{pred['priority']} Priority</span></p>
                    <p style="margin: 4px 0;"><b>Assigned Department:</b> <b>{pred['department']}</b></p>
                    <p style="margin: 4px 0;"><b>Target Response SLA:</b> {4 if pred['priority'] == 'High' else (24 if pred['priority'] == 'Medium' else 72)} hours</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please provide details for your complaint.")

    # --- TAB 2: TRACK MY COMPLAINTS ---
    with cust_tab2:
        st.subheader("Your Complaint History & Status Tracker")
        my_tickets = get_customer_complaints(st.session_state.username)

        if not my_tickets:
            st.info("You haven't submitted any complaints yet. Use the 'Raise a New Complaint' tab to submit one.")
        else:
            st.write(f"Showing **{len(my_tickets)}** ticket(s) submitted by your account:")

            for t in my_tickets:
                t_id, text, cat, macro_p, prio, dept, status_val, admin_note, created_at, updated_at = t

                prio_cls = f"priority-badge-{prio.lower()}"
                status_cls = f"status-badge-{('progress' if status_val == 'In Progress' else status_val.lower())}"

                # Calculate progress bar percentage
                pct = 0.25 if status_val == "Pending" else (0.65 if status_val == "In Progress" else 1.0)

                with st.container():
                    st.markdown(f"""
                    <div class="ticket-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">Ticket #{t_id:03d} • {cat.replace('_', ' ').title()}</span>
                            <div>
                                <span class="{prio_cls}">{prio} Priority</span> &nbsp;
                                <span class="{status_cls}">{status_val}</span>
                            </div>
                        </div>
                        <p style="color: #334155; margin-bottom: 10px; font-size: 0.95rem;">"{text}"</p>
                        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">
                            <span>🏢 <b>Department:</b> {dept}</span> &nbsp;|&nbsp;
                            <span>📅 <b>Submitted:</b> {created_at}</span> &nbsp;|&nbsp;
                            <span>🔄 <b>Last Updated:</b> {updated_at}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.progress(pct, text=f"Status: {status_val} (Stage {1 if status_val == 'Pending' else (2 if status_val == 'In Progress' else 3)} of 3)")

                    # Admin response note callout
                    if status_val == "Resolved":
                        st.success(f"**Resolution Note:** {admin_note}")
                    elif status_val == "In Progress":
                        st.info(f"**Active Status:** {admin_note}")
                    else:
                        st.warning(f"**Current Status:** {admin_note}")

                    st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# VIEW 3: ADMIN ROLE (ALL TICKETS, POWER BI, HIVE LAKE, ML BENCHMARKS)
# ==============================================================================
elif st.session_state.role == "admin":
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs([
        "📂 All Complaints Triage",
        "📊 Power BI & Analytics",
        "🗄️ Apache Hive Data Lake",
        "🤖 ML Model Benchmarks",
        "⚡ Admin Data Controls"
    ])

    # --- ADMIN TAB 1: ALL COMPLAINTS TRIAGE ---
    with adm_tab1:
        st.subheader("Customer Complaint Tickets Management")

        # Filters row
        f1, f2, f3 = st.columns(3)
        with f1:
            f_status = st.selectbox("Status Filter:", ["All", "Pending", "In Progress", "Resolved"])
        with f2:
            f_prio = st.selectbox("Priority Filter:", ["All", "High", "Medium", "Low"])
        with f3:
            f_search = st.text_input("Search Customer / Keyword / ID:", "")

        all_tickets = get_all_complaints(status_filter=f_status, priority_filter=f_prio)
        if f_search.strip():
            kw = f_search.strip().lower()
            all_tickets = [t for t in all_tickets if kw in str(t[0]) or kw in t[1].lower() or kw in t[2].lower() or kw in t[3].lower()]

        st.caption(f"Displaying **{len(all_tickets)}** complaints matching criteria")

        for ticket in all_tickets:
            t_id, cust_user, text, cat, macro_p, prio, dept, status_val, admin_note, created_at, updated_at = ticket

            prio_cls = f"priority-badge-{prio.lower()}"
            status_cls = f"status-badge-{('progress' if status_val == 'In Progress' else status_val.lower())}"

            with st.expander(f"Ticket #{t_id:03d} | Customer: @{cust_user} | [{prio}] {cat.replace('_', ' ').title()} | Status: {status_val}"):
                c_left, c_right = st.columns([3, 2])

                with c_left:
                    st.markdown(f"**Narrative:** \"{text}\"")
                    st.markdown(f"""
                    - **Category:** `{cat}`
                    - **Financial Product:** {macro_p}
                    - **Assigned Department:** **{dept}**
                    - **Registered On:** {created_at} (Last updated: {updated_at})
                    """)

                with c_right:
                    st.markdown("##### Update Status & Resolution Note")
                    status_choices = ["Pending", "In Progress", "Resolved"]
                    curr_idx = status_choices.index(status_val) if status_val in status_choices else 0
                    new_status = st.selectbox("Update Status:", status_choices, index=curr_idx, key=f"adm_st_{t_id}")

                    new_note = st.text_area(
                        "Official Resolution Note to Customer:",
                        value=admin_note if admin_note else "",
                        key=f"adm_note_{t_id}",
                        height=85
                    )

                    if st.button("💾 Save Update", key=f"adm_save_{t_id}", type="primary"):
                        update_complaint_status_and_notes(t_id, new_status, new_note.strip())
                        sync_hive_warehouse()
                        export_powerbi_star_schema()
                        st.success(f"Ticket #{t_id} updated to '{new_status}'!")
                        st.rerun()

    # --- ADMIN TAB 2: POWER BI & ANALYTICS ---
    with adm_tab2:
        st.subheader("Executive Business Intelligence & Power BI Dashboard")
        stats = get_stats()

        # Scorecard Row
        k1, k2, k3, k4 = st.columns(4)
        tot = stats["total"]
        res = stats["resolved"]
        pend = stats["pending"]
        hp = stats["high_priority"]
        res_rate = round((res / tot * 100), 1) if tot else 0

        k1.metric("Total Complaints Ingested", f"{tot:,}")
        k2.metric("Resolution SLA %", f"{res_rate}%", delta=f"{res} resolved")
        k3.metric("Critical High Urgency", f"{hp}", delta=f"{round(hp/tot*100, 1) if tot else 0}% share", delta_color="inverse")
        k4.metric("Pending Backlog", f"{pend}", delta=f"{stats['in_progress']} in progress")

        st.markdown("---")
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown("##### 🏢 Department Workload Distribution")
            dept_dict = stats["department_breakdown"]
            if dept_dict:
                d_df = pd.DataFrame(list(dept_dict.items()), columns=["Department", "Complaints"])
                st.bar_chart(d_df.set_index("Department"), color="#2563eb")

        with ch2:
            st.markdown("##### 🏷️ Top Complaint Categories")
            top_cats = stats["top_categories"]
            if top_cats:
                c_df = pd.DataFrame(top_cats)
                c_df["Category Name"] = c_df["category"].str.replace("_", " ").str.title()
                st.bar_chart(c_df.set_index("Category Name")["count"], color="#059669")

        st.markdown("---")
        st.markdown("##### 📥 Exported Power BI Star Schema Tables")
        b1, b2 = st.columns([1, 2])
        with b1:
            st.markdown("""
            - `data/powerbi/fact_complaints.csv`
            - `data/powerbi/dim_category.csv`
            - `data/powerbi/dim_department.csv`
            - `data/powerbi/dim_priority.csv`
            - `data/powerbi/kpi_summary.csv`
            """)
            if st.button("🔄 Re-Export Power BI Star Schema"):
                export_powerbi_star_schema()
                st.success("Power BI tables refreshed!")
        with b2:
            st.code("""
// Power BI DAX Expression: Resolution Rate %
Resolution Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_complaints), fact_complaints[status] = "Resolved"),
    COUNTROWS(fact_complaints),
    0
) * 100
            """, language="dax")

    # --- ADMIN TAB 3: APACHE HIVE DATA LAKE ---
    with adm_tab3:
        st.subheader("Apache Hive / Hadoop Data Lake Warehouse")
        st.markdown("""
        Simulated HDFS storage layout: `warehouse/tablespace/external/hive/status={status}/priority={priority}/part-00000.csv`
        """)

        h_queries = [
            ("department_kpis", "Query 1: Department Workload & Resolution SLA Breakdown"),
            ("high_risk_backlog", "Query 2: High-Urgency Unresolved Fraud / Stolen Incidents"),
            ("category_volume_pareto", "Query 3: Category Volume Ranking & Percent Share (Pareto Analysis)"),
            ("all", "Query 4: Master Partitioned Hive Table View")
        ]
        q_sel = st.selectbox("Select HiveQL Query:", h_queries, format_func=lambda x: x[1])

        if st.button("⚡ Execute HiveQL Query"):
            res_df = execute_hive_query(q_sel[0])
            st.success(f"Returned {len(res_df)} rows from warehouse tables.")
            st.dataframe(res_df, use_container_width=True)

    # --- ADMIN TAB 4: ML MODEL BENCHMARKS ---
    with adm_tab4:
        st.subheader("Machine Learning Benchmark (5 Models)")
        comp_path = "artifacts/model_comparison.json"
        if os.path.exists(comp_path):
            with open(comp_path, "r") as f:
                c_data = json.load(f)
            c_df = pd.DataFrame(c_data)
            c_df["Accuracy (%)"] = (c_df["accuracy"] * 100).round(2)
            c_df["F1 Macro"] = c_df["f1_macro"]
            c_df["Precision"] = c_df["precision_macro"]
            c_df["Recall"] = c_df["recall_macro"]
            c_df["Latency (ms)"] = c_df["latency_ms_per_sample"]
            show_cols = ["model_name", "Accuracy (%)", "F1 Macro", "Precision", "Recall", "Latency (ms)"]
            st.dataframe(c_df[show_cols].sort_values(by="Accuracy (%)", ascending=False), use_container_width=True)

        img_c1, img_c2 = st.columns(2)
        with img_c1:
            st.markdown("##### Model Accuracy & F1 Bar Chart")
            if os.path.exists("artifacts/model_comparison_chart.png"):
                st.image("artifacts/model_comparison_chart.png", use_container_width=True)
        with img_c2:
            st.markdown("##### Normalized Confusion Matrix")
            if os.path.exists("artifacts/confusion_matrix.png"):
                st.image("artifacts/confusion_matrix.png", use_container_width=True)

    # --- ADMIN TAB 5: ADMIN DATA CONTROLS ---
    with adm_tab5:
        st.subheader("Administrative Controls & Demo Tools")
        st.write("Use these controls to reset demo data before your presentation.")

        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            if st.button("🔄 Reseed Sample Complaints & Sync Warehouses", type="primary"):
                seed_database(reset=True)
                st.success("Sample data reseeded and synchronized!")
                st.rerun()

        with ctrl_col2:
            st.markdown("""
            **Demo Users Available:**
            - **Customer 1**: Username `user` | Password `user123`
            - **Customer 2**: Username `john_doe` | Password `pass123`
            - **Admin**: Username `admin` | Password `admin123`
            """)