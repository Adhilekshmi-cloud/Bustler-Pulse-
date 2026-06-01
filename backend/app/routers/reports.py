from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models import Report, Ticket
from app.schemas import ReportResponse
from app.services.report_generator import analyse_patterns, get_heatmap_data

router = APIRouter(prefix="/reports", tags=["Reports"])


# ── GET /reports ─────────────────────────────────────────
# Returns all micro-reports grouped by category
# Used by your product feedback page
# Shows which issues are most common → product team fixes them

@router.get("/")
def get_reports(db: Session = Depends(get_db)):
    patterns = analyse_patterns(db)

    return {
        "total_reports" : db.query(Report).count(),
        "generated_at"  : datetime.utcnow().isoformat(),
        "patterns"      : patterns
    }


# ── GET /reports/all ─────────────────────────────────────
# Returns every individual report ever created
# Full list for the ops team to review

@router.get("/all", response_model=List[ReportResponse])
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return reports


# ── GET /reports/heatmap ─────────────────────────────────
# Returns ticket counts grouped by category and week
# Used by your heatmap UI page
# Shows spikes — e.g. payment issues always spike in week 3

@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    heatmap_data = get_heatmap_data(db)

    return {
        "generated_at" : datetime.utcnow().isoformat(),
        "heatmap"      : heatmap_data
    }


# ── GET /reports/summary ─────────────────────────────────
# Quick summary card for the ops dashboard
# Shows key numbers at a glance

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    today = date.today()

    total_tickets    = db.query(Ticket).count()
    open_tickets     = db.query(Ticket).filter(Ticket.status == "open").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved").count()
    critical_tickets = db.query(Ticket).filter(Ticket.urgency == "critical").count()
    anger_flagged    = db.query(Ticket).filter(Ticket.is_anger_flagged == 1).count()

    resolved_today = db.query(Ticket).filter(
        Ticket.status == "resolved",
        Ticket.resolved_at >= datetime.combine(today, datetime.min.time())
    ).count()

    total_reports = db.query(Report).count()

    avg_csat = None
    csat_scores = db.query(Report.csat_score).filter(
        Report.csat_score != None
    ).all()
    if csat_scores:
        avg_csat = round(
            sum(s[0] for s in csat_scores) / len(csat_scores), 1
        )

    return {
        "total_tickets"   : total_tickets,
        "open_tickets"    : open_tickets,
        "resolved_tickets": resolved_tickets,
        "critical_tickets": critical_tickets,
        "anger_flagged"   : anger_flagged,
        "resolved_today"  : resolved_today,
        "total_reports"   : total_reports,
        "avg_csat"        : avg_csat,
        "generated_at"    : datetime.utcnow().isoformat()
    }


# ── GET /reports/{ticket_id} ─────────────────────────────
# Get the micro-report for a specific ticket
# Used by Anjali (user tracking) and Ambadi (agent view)