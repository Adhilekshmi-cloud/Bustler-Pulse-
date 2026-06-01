from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Report, Ticket

# ── Micro Report Generator ──────────────────────────────
# Called automatically every time a ticket is resolved
# Creates a structured report: what broke, why, how fixed
# These reports pile up over time and feed the product team

def generate_report(
    db: Session,
    ticket: Ticket,
    resolution_notes: str,
    what_broke: str,
    why_it_happened: str = None,
    how_fixed: str = None,
    csat_score: int = None
) -> Report:
    """
    Auto-generates a micro-report when a ticket is resolved.
    Called inside PATCH /ticket/resolve endpoint.
    """

    report = Report(
        ticket_id       = ticket.id,
        category        = ticket.category,
        what_broke      = what_broke,
        why_it_happened = why_it_happened,
        how_fixed       = how_fixed,
        csat_score      = csat_score,
        created_at      = datetime.utcnow()
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# ── Pattern Analyser ────────────────────────────────────
# Reads all reports and finds recurring issues
# Output goes to the product feedback page

def analyse_patterns(db: Session) -> list:
    """
    Groups all reports by category and counts occurrences.
    Returns a ranked list of most common issues.
    Used by GET /reports endpoint.
    """
    from sqlalchemy import func
    from app.models import Report

    results = (
        db.query(
            Report.category,
            func.count(Report.id).label("total"),
            func.avg(Report.csat_score).label("avg_csat")
        )
        .group_by(Report.category)
        .order_by(func.count(Report.id).desc())
        .all()
    )

    patterns = []
    for row in results:
        patterns.append({
            "category"    : row.category,
            "total_issues": row.total,
            "avg_csat"    : round(row.avg_csat, 1) if row.avg_csat else None,
            "priority"    : get_priority_label(row.total)
        })

    return patterns


# ── Heatmap Data ─────────────────────────────────────────
# Returns issue counts grouped by category and week
# Used by GET /heatmap endpoint → your heatmap UI

def get_heatmap_data(db: Session) -> list:
    """
    Returns ticket counts grouped by category and week number.
    Used to show which issues spike at which time of month.
    """
    from sqlalchemy import func, extract
    from app.models import Ticket

    results = (
        db.query(
            Ticket.category,
            extract("week", Ticket.created_at).label("week"),
            func.count(Ticket.id).label("count")
        )
        .group_by(Ticket.category, "week")
        .order_by("week")
        .all()
    )

    heatmap = []
    for row in results:
        heatmap.append({
            "category": row.category,
            "week"    : int(row.week),
            "count"   : row.count
        })

    return heatmap


# ── Priority Label Helper ────────────────────────────────
def get_priority_label(count: int) -> str:
    """
    Converts issue count into a priority label
    for the product feedback page.
    """
    if count >= 10:
        return "🔴 High Priority — fix in app immediately"
    elif count >= 5:
        return "🟡 Medium Priority — investigate root cause"
    else:
        return "🟢 Low Priority — monitor"