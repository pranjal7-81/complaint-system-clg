import os
import sqlite3
import json
import warnings
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.predict import predict_complaint
from src.hive_analytics import execute_hive_query, sync_hive_warehouse
from src.powerbi_export import export_powerbi_star_schema
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

warnings.filterwarnings('ignore')

DB_PATH = "complaints.db"
MODEL_COMPARISON_PATH = "artifacts/model_comparison.json"

app = FastAPI(
    title="Customer Complaint Intelligence & Big Data API",
    version="3.0.0",
    description="Enterprise API for Complaint Classification, Big Data Analytics (Spark/Hive), and Power BI Reporting"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ComplaintSubmitRequest(BaseModel):
    customer_username: str = "user"
    complaint: str


class StatusUpdateRequest(BaseModel):
    status: str
    admin_notes: str = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str


@app.on_event("startup")
def startup_event():
    create_database()
    sync_hive_warehouse()


@app.get("/")
def root():
    return {
        "message": "Customer Complaint Intelligence & Big Data Platform API v3.0",
        "status": "online",
        "technologies": ["Apache Spark / PySpark", "Apache Hive / Hadoop", "Power BI", "FastAPI", "Streamlit"]
    }


@app.post("/api/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if user:
        return {"success": True, "user": user, "token": f"auth-{user['username']}-token"}
    raise HTTPException(status_code=401, detail="Invalid username or password.")


@app.post("/api/register")
def register(req: RegisterRequest):
    ok, msg = register_user(req.username, req.password, req.full_name, role="customer")
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.get("/api/customer/{username}/complaints")
def get_customer_tickets(username: str):
    rows = get_customer_complaints(username)
    return [
        {
            "id": r[0],
            "complaint": r[1],
            "category": r[2],
            "macro_product": r[3],
            "priority": r[4],
            "department": r[5],
            "status": r[6],
            "admin_notes": r[7],
            "created_at": r[8],
            "updated_at": r[9]
        }
        for r in rows
    ]


@app.get("/api/complaints")
def get_admin_complaints(status: str = None, priority: str = None, department: str = None):
    rows = get_all_complaints(status_filter=status, priority_filter=priority, department_filter=department)
    return [
        {
            "id": r[0],
            "customer_username": r[1],
            "complaint": r[2],
            "category": r[3],
            "macro_product": r[4],
            "priority": r[5],
            "department": r[6],
            "status": r[7],
            "admin_notes": r[8],
            "created_at": r[9],
            "updated_at": r[10]
        }
        for r in rows
    ]


@app.post("/api/complaints")
def submit_complaint(req: ComplaintSubmitRequest):
    text = req.complaint.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty.")

    pred = predict_complaint(text)
    new_id = add_complaint(
        customer_username=req.customer_username,
        complaint=text,
        category=pred["category"],
        macro_product=pred["macro_product"],
        priority=pred["priority"],
        department=pred["department"],
        status="Pending",
        admin_notes="Ticket queued for investigation."
    )

    sync_hive_warehouse()
    export_powerbi_star_schema()

    return {
        "success": True,
        "id": new_id,
        "customer_username": req.customer_username,
        "complaint": text,
        "category": pred["category"],
        "macro_product": pred["macro_product"],
        "priority": pred["priority"],
        "department": pred["department"],
        "status": "Pending"
    }


@app.patch("/api/complaints/{complaint_id}/status")
def update_status(complaint_id: int, req: StatusUpdateRequest):
    if req.status not in ["Pending", "In Progress", "Resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status.")
    update_complaint_status_and_notes(complaint_id, req.status, req.admin_notes)
    sync_hive_warehouse()
    export_powerbi_star_schema()
    return {"success": True, "id": complaint_id, "status": req.status, "admin_notes": req.admin_notes}


@app.get("/api/stats")
def get_analytics():
    return get_stats()


@app.get("/api/models")
def get_model_benchmarks():
    if os.path.exists(MODEL_COMPARISON_PATH):
        with open(MODEL_COMPARISON_PATH, "r") as f:
            return json.load(f)
    return []


@app.get("/api/hive/query")
def get_hive_query_results(query: str = "department_kpis"):
    df = execute_hive_query(query)
    return df.to_dict(orient="records")


@app.post("/api/powerbi/export")
def trigger_powerbi_export():
    export_powerbi_star_schema()
    return {"success": True, "message": "Power BI star schema exported to data/powerbi/"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
