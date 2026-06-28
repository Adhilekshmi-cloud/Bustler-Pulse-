from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models import Report, Ticket
from app.schemas import ReportResponse
from app.services.report_generator import analyse_patterns, get_heatmap_data

from fastapi.responses import FileResponse
from app.services.pdf_export import build_analytics_pdf
import os
import tempfile

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def get_reports(db: Session = Depends(get_db)):
    patterns = analyse_patterns(db)
    return {
        "total_reports" : db.query(Report).count(),
        "generated_at"  : datetime.utcnow().isoformat(),
        "patterns"      : patterns
    }


@router.get("/all", response_model=List[ReportResponse])
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return reports


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    heatmap_data = get_heatmap_data(db)
    return {
        "generated_at" : datetime.utcnow().isoformat(),
        "heatmap"      : heatmap_data
    }

@router.get("/export-pdf")
def export_pdf(db: Session = Depends(get_db)):
    patterns = analyse_patterns(db)
    heatmap_data = get_heatmap_data(db)

    today = date.today()
    total_tickets    = db.query(Ticket).count()
    open_tickets     = db.query(Ticket).filter(Ticket.status == "open").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved").count()
    critical_tickets = db.query(Ticket).filter(Ticket.urgency == "critical").count()
    anger_flagged    = db.query(Ticket).filter(Ticket.is_anger_flagged == 1).count()
    resolved_today   = db.query(Ticket).filter(
        Ticket.status == "resolved",
        Ticket.resolved_at >= datetime.combine(today, datetime.min.time())
    ).count()
    total_reports = db.query(Report).count()

    avg_csat = None
    csat_scores = db.query(Report.csat_score).filter(Report.csat_score != None).all()
    if csat_scores:
        avg_csat = round(sum(s[0] for s in csat_scores) / len(csat_scores), 1)

    summary = {
        "total_tickets"   : total_tickets,
        "open_tickets"    : open_tickets,
        "resolved_tickets": resolved_tickets,
        "critical_tickets": critical_tickets,
        "anger_flagged"   : anger_flagged,
        "resolved_today"  : resolved_today,
        "total_reports"   : total_reports,
        "avg_csat"        : avg_csat
    }

    output_path = os.path.join(tempfile.gettempdir(), "bustler_pulse_report.pdf")
    build_analytics_pdf(output_path, summary, patterns, heatmap_data)

    return FileResponse(
        path      = output_path,
        filename  = "bustler_pulse_report.pdf",
        media_type= "application/pdf"
    )

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


@router.get("/detailed")
def get_detailed_reports(db: Session = Depends(get_db)):
    from app.models import Agent
    reports = db.query(Report).order_by(Report.created_at.desc()).all()

    detailed = []
    for r in reports:
        ticket = db.query(Ticket).filter(Ticket.id == r.ticket_id).first()

        agent_name = "Unassigned"
        if ticket and ticket.assigned_agent_id:
            agent = db.query(Agent).filter(
                Agent.id == ticket.assigned_agent_id
            ).first()
            if agent:
                agent_name = agent.name

        detailed.append({
            "report_id"      : r.id,
            "ticket_id"      : r.ticket_id,
            "category"       : r.category,
            "what_broke"     : r.what_broke,
            "why_it_happened": r.why_it_happened,
            "how_fixed"      : r.how_fixed,
            "csat_score"     : r.csat_score,
            "resolved_by"    : agent_name,
            "resolved_at"    : r.created_at.isoformat(),
            "user_id"        : ticket.user_id if ticket else "unknown",
            "description"    : ticket.description if ticket else "—"
        })

    return {
        "total"   : len(detailed),
        "reports" : detailed
    }


@router.get("/{ticket_id}", response_model=ReportResponse)
def get_report_by_ticket(ticket_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    report = db.query(Report).filter(
        Report.ticket_id == ticket_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="No report found for this ticket yet"
        )
    return report