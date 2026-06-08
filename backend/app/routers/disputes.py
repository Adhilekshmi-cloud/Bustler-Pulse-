from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Dispute, Ticket
from app.schemas import DisputeCreate, DisputeResponse

router = APIRouter(prefix="/disputes", tags=["Disputes"])


# ── POST /disputes/ ──────────────────────────────────────
# Anjali's dispute center calls this
# Creates a dispute linked to an existing ticket

@router.post("/", response_model=DisputeResponse)
def create_dispute(dispute_data: DisputeCreate, db: Session = Depends(get_db)):
    # Check ticket exists
    ticket = db.query(Ticket).filter(
        Ticket.id == dispute_data.ticket_id
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check if dispute already exists for this ticket
    existing = db.query(Dispute).filter(
        Dispute.ticket_id == dispute_data.ticket_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dispute already exists for this ticket")

    dispute = Dispute(
        ticket_id    = dispute_data.ticket_id,
        raised_by    = dispute_data.raised_by,
        against      = dispute_data.against,
        evidence_url = dispute_data.evidence_url,
        status       = "open",
        created_at   = datetime.utcnow()
    )

    db.add(dispute)

    # Update ticket status to in_progress
    ticket.status = "in_progress"
    db.commit()
    db.refresh(dispute)

    return dispute


# ── GET /disputes/ ───────────────────────────────────────
# List all disputes
# Used by Ambadi's ops dashboard

@router.get("/")
def get_disputes(db: Session = Depends(get_db)):
    disputes = db.query(Dispute).order_by(
        Dispute.created_at.desc()
    ).all()
    return disputes


# ── GET /disputes/{id} ───────────────────────────────────
# Get one dispute by ID

@router.get("/{dispute_id}", response_model=DisputeResponse)
def get_dispute(dispute_id: int, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(
        Dispute.id == dispute_id
    ).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


# ── PATCH /disputes/{id}/resolve ─────────────────────────
# Ops agent resolves a dispute

@router.patch("/{dispute_id}/resolve", response_model=DisputeResponse)
def resolve_dispute(
    dispute_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db)
):
    dispute = db.query(Dispute).filter(
        Dispute.id == dispute_id
    ).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    dispute.status           = "resolved"
    dispute.resolution_notes = resolution_notes
    db.commit()
    db.refresh(dispute)

    return dispute