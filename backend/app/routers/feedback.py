from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Feedback, Ticket
from app.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])


# ── POST /feedback ───────────────────────────────────────
# Anjali's resolution survey submits here
# Called after a ticket is resolved

@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db)
):
    # Check ticket exists
    ticket = db.query(Ticket).filter(
        Ticket.id == feedback_data.ticket_id
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check if feedback already exists for this ticket
    existing = db.query(Feedback).filter(
        Feedback.ticket_id == feedback_data.ticket_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Feedback already submitted for this ticket"
        )

    feedback = Feedback(
        ticket_id  = feedback_data.ticket_id,
        user       = feedback_data.user,
        csat_score = feedback_data.csat_score,
        comment    = feedback_data.comment,
        tag        = feedback_data.tag,
        created_at = datetime.utcnow()
    )

    db.add(feedback)

    # Also update the report csat_score if report exists
    from app.models import Report
    report = db.query(Report).filter(
        Report.ticket_id == feedback_data.ticket_id
    ).first()
    if report:
        report.csat_score = feedback_data.csat_score

    db.commit()
    db.refresh(feedback)
    return feedback


# ── GET /feedback ────────────────────────────────────────
# Ambadi's dashboard fetches all feedback
# Shows user satisfaction across all resolved tickets

@router.get("/", response_model=List[FeedbackResponse])
def get_all_feedback(db: Session = Depends(get_db)):
    feedback = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).all()
    return feedback


# ── GET /feedback/{ticket_id} ────────────────────────────
# Get feedback for one specific ticket

@router.get("/{ticket_id}", response_model=FeedbackResponse)
def get_feedback_by_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    feedback = db.query(Feedback).filter(
        Feedback.ticket_id == ticket_id
    ).first()
    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="No feedback found for this ticket"
        )
    return feedback


# ── GET /feedback/summary/stats ──────────────────────────
# Summary stats for Ambadi's dashboard
# Average CSAT, total feedback, tag breakdown

@router.get("/summary/stats")
def get_feedback_summary(db: Session = Depends(get_db)):
    all_feedback = db.query(Feedback).all()

    if not all_feedback:
        return {
            "total_feedback" : 0,
            "avg_csat"       : None,
            "tag_breakdown"  : {},
            "generated_at"   : datetime.utcnow().isoformat()
        }

    avg_csat = round(
        sum(f.csat_score for f in all_feedback) / len(all_feedback), 1
    )

    # Count tags
    tag_breakdown = {}
    for f in all_feedback:
        if f.tag:
            tag_breakdown[f.tag] = tag_breakdown.get(f.tag, 0) + 1

    return {
        "total_feedback" : len(all_feedback),
        "avg_csat"       : avg_csat,
        "tag_breakdown"  : tag_breakdown,
        "generated_at"   : datetime.utcnow().isoformat()
    }