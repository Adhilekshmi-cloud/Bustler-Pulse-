from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models import Ticket
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


# ── GET /health ──────────────────────────────────────────
# Public system health page
# Users see this to know Bustler is actively working
# Stops repeat complaints on the same known issue

@router.get("/", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    today = date.today()

    open_tickets     = db.query(Ticket).filter(
        Ticket.status == "open"
    ).count()

    critical_tickets = db.query(Ticket).filter(
        Ticket.urgency == "critical",
        Ticket.status != "resolved"
    ).count()

    resolved_today   = db.query(Ticket).filter(
        Ticket.status == "resolved",
        Ticket.resolved_at >= datetime.combine(
            today, datetime.min.time()
        )
    ).count()

    # Generate status message based on current load
    if critical_tickets == 0 and open_tickets < 5:
        status  = "operational"
        message = "✅ All systems operational. Support team is available."
    elif critical_tickets > 0 and critical_tickets < 5:
        status  = "degraded"
        message = f"⚠️ {critical_tickets} critical issue(s) being actively worked on."
    else:
        status  = "incident"
        message = f"🔴 High volume of issues detected. Team is on it."

    return HealthResponse(
        status           = status,
        open_tickets     = open_tickets,
        critical_tickets = critical_tickets,
        resolved_today   = resolved_today,
        message          = message
    )


# ── GET /health/detailed ─────────────────────────────────
# Detailed breakdown for the internal ops team
# Not shown publicly — only for Ambadi's dashboard

@router.get("/detailed")
def get_detailed_health(db: Session = Depends(get_db)):
    categories = [
        "payment", "refund", "delivery",
        "quality", "no_response", "other"
    ]

    breakdown = {}
    for cat in categories:
        breakdown[cat] = {
            "open"    : db.query(Ticket).filter(
                Ticket.category == cat,
                Ticket.status   == "open"
            ).count(),
            "resolved": db.query(Ticket).filter(
                Ticket.category == cat,
                Ticket.status   == "resolved"
            ).count(),
            "critical": db.query(Ticket).filter(
                Ticket.category == cat,
                Ticket.urgency  == "critical"
            ).count()
        }

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "breakdown"   : breakdown
    }