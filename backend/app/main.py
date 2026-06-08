from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import tickets, reports, agents, health, disputes

# ── Create all database tables ───────────────────────────
Base.metadata.create_all(bind=engine)

# ── Initialize FastAPI app ───────────────────────────────
app = FastAPI(
    title       = "Bustler Pulse API",
    description = "Intelligent support & operations system for Bustler",
    version     = "1.0.0"
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

# ── Register all routers ─────────────────────────────────
app.include_router(tickets.router)
app.include_router(reports.router)
app.include_router(agents.router)
app.include_router(health.router)
app.include_router(disputes.router)

# ── Root endpoint ────────────────────────────────────────
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