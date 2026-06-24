import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models import Ticket, Agent
from app.schemas import TicketCreate, TicketResolve, TicketResponse
from app.services.triage import triage_ticket, suggest_agent
from app.services.report_generator import generate_report
from app.services.badge import award_badge

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ── POST /tickets ────────────────────────────────────────
@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):

    triage_result = triage_ticket(
        category    = ticket_data.category,
        description = ticket_data.description
    )

    agents = db.query(Agent).all()
    best_agent = suggest_agent(ticket_data.category, agents)

    ticket = Ticket(
        user_id           = ticket_data.user_id,
        project_id        = ticket_data.project_id,
        payment_status    = ticket_data.payment_status,
        category          = ticket_data.category,
        description       = ticket_data.description,
        status            = "open",
        urgency           = triage_result["urgency"],
        is_anger_flagged  = triage_result["is_anger_flagged"],
        auto_reply_sent   = triage_result["auto_reply_sent"],
        assigned_agent_id = best_agent.id if best_agent else None,
        screenshot_url    = ticket_data.screenshot_url,
        created_at        = datetime.utcnow()
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


# ── GET /tickets ─────────────────────────────────────────
@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    status  : Optional[str] = None,
    category: Optional[str] = None,
    urgency : Optional[str] = None,
    db      : Session = Depends(get_db)
):
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if urgency:
        query = query.filter(Ticket.urgency == urgency)

    tickets = query.order_by(
        Ticket.is_anger_flagged.desc(),
        Ticket.urgency.desc(),
        Ticket.created_at.asc()
    ).all()

    return tickets


# ── GET /tickets/orders/{user_id} ───────────────────────
# Returns mock order data for Anjali's order picker
# Will be replaced with real Bustler API when available
# IMPORTANT: must be defined BEFORE /{ticket_id} to avoid route conflict

@router.get("/orders/{user_id}")
def get_user_orders(user_id: str):
    mock_orders = [
        {
            "order_id"        : "BST-2026-0042",
            "project_name"    : "Logo Design for Cafe Mocha",
            "freelancer_name" : "Rahul Menon",
            "amount"          : 2500,
            "status"          : "completed",
            "date"            : "2026-06-15"
        },
        {
            "order_id"        : "BST-2026-0089",
            "project_name"    : "Wedding Photography",
            "freelancer_name" : "Priya Nair",
            "amount"          : 15000,
            "status"          : "in_progress",
            "date"            : "2026-06-18"
        },
        {
            "order_id"        : "BST-2026-0103",
            "project_name"    : "Website Development",
            "freelancer_name" : "Arjun Krishna",
            "amount"          : 8500,
            "status"          : "completed",
            "date"            : "2026-06-10"
        },
        {
            "order_id"        : "BST-2026-0124",
            "project_name"    : "Birthday Cake Order",
            "freelancer_name" : "Lakshmi Bakery",
            "amount"          : 1200,
            "status"          : "delivered",
            "date"            : "2026-06-20"
        },
        {
            "order_id"        : "BST-2026-0156",
            "project_name"    : "Resume Writing Service",
            "freelancer_name" : "Sneha Pillai",
            "amount"          : 800,
            "status"          : "pending",
            "date"            : "2026-06-22"
        },
        {
            "order_id"        : "BST-2026-0178",
            "project_name"    : "Home Cleaning Service",
            "freelancer_name" : "Clean Pro Services",
            "amount"          : 1500,
            "status"          : "completed",
            "date"            : "2026-06-08"
        }
    ]

    return {
        "user_id"      : user_id,
        "total_orders" : len(mock_orders),
        "orders"       : mock_orders
    }


# ── GET /context/{user_id} ───────────────────────────────
# Anjali's ticket form calls this on load
# Returns last known project + payment context for a user

@router.get("/context/{user_id}")
def get_user_context(user_id: str, db: Session = Depends(get_db)):
    last_ticket = db.query(Ticket).filter(
        Ticket.user_id == user_id
    ).order_by(Ticket.created_at.desc()).first()

    if last_ticket:
        return {
            "user_id"       : user_id,
            "project_id"    : last_ticket.project_id,
            "payment_status": last_ticket.payment_status,
            "last_category" : last_ticket.category,
            "found"         : True
        }

    return {
        "user_id"       : user_id,
        "project_id"    : None,
        "payment_status": None,
        "last_category" : None,
        "found"         : False
    }


# ── POST /tickets/upload-screenshot ─────────────────────
# Uploads image to Cloudinary — permanent storage

@router.post("/upload-screenshot")
async def upload_screenshot(file: UploadFile = File(...)):
    import cloudinary
    import cloudinary.uploader
    import io

    cloudinary.config(
        cloud_name = "dxykbg56j",
        api_key    = "351331374515618",
        api_secret = "JXD0X2Yy7qS1gLzSm81qJQ-xYFo"
    )

    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed (jpeg, png, gif, webp)"
        )

    contents = await file.read()

    result = cloudinary.uploader.upload(
        io.BytesIO(contents),
        folder        = "bustler-pulse",
        resource_type = "image"
    )

    return {
        "screenshot_url": result["secure_url"],
        "filename"      : result["public_id"],
        "message"       : "Screenshot uploaded successfully to Cloudinary"
    }


# ── GET /tickets/{id} ────────────────────────────────────
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# ── PATCH /tickets/{id}/resolve ──────────────────────────
@router.patch("/{ticket_id}/resolve", response_model=TicketResponse)
def resolve_ticket(
    ticket_id       : int,
    resolution_data : TicketResolve,
    db              : Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status == "resolved":
        raise HTTPException(status_code=400, detail="Ticket already resolved")

    ticket.status      = "resolved"
    ticket.resolved_at = datetime.utcnow()
    db.commit()

    generate_report(
        db               = db,
        ticket           = ticket,
        resolution_notes = resolution_data.resolution_notes,
        what_broke       = resolution_data.what_broke,
        why_it_happened  = resolution_data.why_it_happened,
        how_fixed        = resolution_data.how_fixed,
        csat_score       = resolution_data.csat_score
    )

    award_badge(db=db, ticket=ticket)

    if ticket.assigned_agent_id:
        agent = db.query(Agent).filter(
            Agent.id == ticket.assigned_agent_id
        ).first()
        if agent:
            agent.tickets_solved += 1
            if resolution_data.csat_score:
                agent.avg_csat = round(
                    (agent.avg_csat * (agent.tickets_solved - 1) +
                     resolution_data.csat_score) / agent.tickets_solved
                )
            db.commit()

    db.refresh(ticket)
    return ticket


# ── GET /tickets/{id}/autoreply ──────────────────────────
@router.get("/{ticket_id}/autoreply")
def get_autoreply(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.auto_reply_sent:
        return {
            "auto_reply_sent": True,
            "message": "Your issue has been identified. Please see the suggested resolution below.",
        }
    return {
        "auto_reply_sent": False,
        "message": "Your ticket has been received and assigned to an agent."
    }
# ── PATCH /tickets/{id}/escalate ─────────────────────────
# Ambadi's ops dashboard calls this to escalate a ticket
# Updates status to in_progress, category to Dispute
# Routes to Anjali P Remesh as escalation handler

from pydantic import BaseModel

class EscalateRequest(BaseModel):
    reason: str

@router.patch("/{ticket_id}/escalate")
def escalate_ticket(
    ticket_id     : int,
    escalate_data : EscalateRequest,
    db            : Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status == "resolved":
        raise HTTPException(
            status_code=400,
            detail="Cannot escalate a resolved ticket"
        )

    # Update ticket fields
    ticket.status   = "in_progress"
    ticket.category = "Dispute"

    db.commit()
    db.refresh(ticket)

    # Build response
    return {
        "id"                : ticket.id,
        "status"            : ticket.status,
        "category"          : ticket.category,
        "escalated_to"      : "Anjali P Remesh",
        "reason"            : escalate_data.reason,
        "user_id"           : ticket.user_id,
        "project_id"        : ticket.project_id,
        "payment_status"    : ticket.payment_status,
        "description"       : ticket.description,
        "urgency"           : ticket.urgency,
        "is_anger_flagged"  : ticket.is_anger_flagged,
        "auto_reply_sent"   : ticket.auto_reply_sent,
        "assigned_agent_id" : ticket.assigned_agent_id,
        "screenshot_url"    : ticket.screenshot_url,
        "created_at"        : ticket.created_at,
        "resolved_at"       : ticket.resolved_at,
        "message"           : "✅ Ticket escalated successfully — routed to Anjali P Remesh"
    }