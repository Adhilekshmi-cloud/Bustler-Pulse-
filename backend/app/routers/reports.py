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

@router.get("/daily-summary-email")
def send_daily_summary_email(db: Session = Depends(get_db)):
    import os
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        return {"error": "SENDGRID_API_KEY not configured"}

    today = date.today()
    today_str = today.strftime("%B %d, %Y")

    # Count unresolved tickets
    unresolved = db.query(Ticket).filter(
        Ticket.status != "resolved"
    ).count()

    open_tickets = db.query(Ticket).filter(
        Ticket.status == "open"
    ).count()

    in_progress = db.query(Ticket).filter(
        Ticket.status == "in_progress"
    ).count()

    critical_unresolved = db.query(Ticket).filter(
        Ticket.status != "resolved",
        Ticket.urgency == "critical"
    ).count()

    anger_flagged = db.query(Ticket).filter(
        Ticket.status != "resolved",
        Ticket.is_anger_flagged == 1
    ).count()

    resolved_today = db.query(Ticket).filter(
        Ticket.status == "resolved",
        Ticket.resolved_at >= datetime.combine(today, datetime.min.time())
    ).count()

    # Determine status label
    if critical_unresolved == 0 and unresolved < 5:
        status_label = "✅ All Clear"
        status_color = "#16a34a"
    elif critical_unresolved > 0:
        status_label = "🔴 Needs Attention"
        status_color = "#E8232A"
    else:
        status_label = "⚠️ Moderate Load"
        status_color = "#f59e0b"

    body_html = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
      <div style="background: #E8232A; padding: 20px 24px; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 20px;">🧠 Bustler Pulse — Daily Summary</h1>
        <p style="color: rgba(255,255,255,0.85); margin: 6px 0 0; font-size: 14px;">{today_str}</p>
      </div>

      <div style="background: white; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 12px 12px;">

        <div style="background: #f9fafb; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px; border-left: 4px solid {status_color};">
          <div style="font-size: 18px; font-weight: 700; color: {status_color};">{status_label}</div>
          <div style="font-size: 13px; color: #666; margin-top: 4px;">End-of-day status for {today_str}</div>
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
          <tr style="background: #f3f4f6;">
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 600; color: #444;">Metric</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 600; color: #444; text-align: right;">Count</td>
          </tr>
          <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 12px 16px; font-size: 14px; color: #555;">Total Unresolved Tickets</td>
            <td style="padding: 12px 16px; font-size: 18px; font-weight: 800; color: #E8232A; text-align: right;">{unresolved}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f3f4f6; background: #fafafa;">
            <td style="padding: 12px 16px; font-size: 14px; color: #555;">— Open (not yet assigned)</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #f59e0b; text-align: right;">{open_tickets}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 12px 16px; font-size: 14px; color: #555;">— In Progress</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #6366f1; text-align: right;">{in_progress}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f3f4f6; background: #fafafa;">
            <td style="padding: 12px 16px; font-size: 14px; color: #555;">Critical & Unresolved</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #E8232A; text-align: right;">{critical_unresolved}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 12px 16px; font-size: 14px; color: #555;">Anger-Flagged & Unresolved</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #f97316; text-align: right;">{anger_flagged}</td>
          </tr>
          <tr style="background: #f0fdf4;">
            <td style="padding: 12px 16px; font-size: 14px; color: #16a34a; font-weight: 600;">✅ Resolved Today</td>
            <td style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #16a34a; text-align: right;">{resolved_today}</td>
          </tr>
        </table>

        <div style="text-align: center; margin-top: 16px;">
          <a href="https://bustler-pulse.vercel.app" style="background: #E8232A; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 14px;">View Full Dashboard →</a>
        </div>

        <p style="font-size: 12px; color: #aaa; text-align: center; margin-top: 24px;">
          — Bustler Pulse Automated Reporting · Sent daily at 6PM IST
        </p>
      </div>
    </div>
    """

    try:
        message = Mail(
            from_email='ambadisoumya188@gmail.com',
            to_emails='ambadisoumya188@gmail.com',
            subject=f'📊 Bustler Pulse Daily Summary — {today_str} ({unresolved} unresolved)',
            html_content=body_html
        )
        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)

        return {
            "message": "✅ Daily summary email sent successfully",
            "date": today_str,
            "unresolved_tickets": unresolved,
            "critical_unresolved": critical_unresolved,
            "resolved_today": resolved_today
        }
    except Exception as e:
        return {"error": f"Email failed: {str(e)}"}
    
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