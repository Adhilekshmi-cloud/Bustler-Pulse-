from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import tickets, reports, agents, health, disputes, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title       = "Bustler Pulse API",
    description = "Intelligent support & operations system for Bustler",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = [
        "*",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://bustler-frontend.vercel.app",
        "https://bustler-pulse-six.vercel.app",
        "https://bustler-pulse.vercel.app"
    ],
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