from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import tickets, reports, agents, health, disputes, auth, feedback

Base.metadata.create_all(bind=engine)
# One-time column additions for new ticket fields
# Safe to run multiple times — uses IF NOT EXISTS
from sqlalchemy import text
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS order_id VARCHAR;"))
        conn.execute(text("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS order_amount INTEGER;"))
        conn.execute(text("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS freelancer_name VARCHAR;"))
        conn.execute(text("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS route_to VARCHAR;"))
        conn.commit()
        print("✅ Columns added/verified successfully")
    except Exception as e:
        print(f"⚠️ Column addition error: {e}")
app = FastAPI(
    title       = "Bustler Pulse API",
    description = "Intelligent support & operations system for Bustler",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

app.include_router(tickets.router)
app.include_router(reports.router)
app.include_router(agents.router)
app.include_router(health.router)
app.include_router(disputes.router)
app.include_router(auth.router)
app.include_router(feedback.router)

@app.get("/")
def root():
    return {
        "project" : "Bustler Pulse",
        "version" : "1.0.0",
        "status"  : "running",
        "team"    : [
            "Adhilekshmi — Intelligence layer",
            "Ambadi      — Ops layer",
            "Anjali      — User layer"
        ],
        "docs"    : "/docs"
    }