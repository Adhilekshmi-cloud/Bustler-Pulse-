from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Agent, Ticket
from app.schemas import AgentCreate, AgentResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


# ── POST /agents ─────────────────────────────────────────
# Create a new ops agent profile
# Ambadi calls this to register agents into the system

@router.post("/", response_model=AgentResponse)
def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    # Check if agent already exists
    existing = db.query(Agent).filter(
        Agent.email == agent_data.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Agent with this email already exists"
        )

    agent = Agent(
        name      = agent_data.name,
        email     = agent_data.email,
        specialty = agent_data.specialty
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


# ── GET /agents ──────────────────────────────────────────
# List all agents with their performance stats
# Used by Ambadi's ops dashboard

@router.get("/", response_model=List[AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(
        Agent.avg_csat.desc()
    ).all()
    return agents


# ── GET /agents/{id} ─────────────────────────────────────
# Get one agent's full profile
# Shows their stats: speed, CSAT, specialty, tickets solved

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# ── GET /agents/{id}/tickets ─────────────────────────────
# Get all tickets assigned to one agent
# Used by the agent to see their own workload

@router.get("/{agent_id}/tickets")
def get_agent_tickets(
    agent_id: int,
    status: str = None,
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    query = db.query(Ticket).filter(
        Ticket.assigned_agent_id == agent_id
    )
    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.order_by(
        Ticket.is_anger_flagged.desc(),
        Ticket.urgency.desc(),
        Ticket.created_at.asc()
    ).all()

    return {
        "agent"         : agent.name,
        "specialty"     : agent.specialty,
        "tickets_solved": agent.tickets_solved,
        "avg_csat"      : agent.avg_csat,
        "tickets"       : tickets
    }


# ── GET /agents/leaderboard ──────────────────────────────
# Shows top performing agents ranked by CSAT + tickets solved
# Makes agents competitive — just like freelancers on Bustler

@router.get("/leaderboard/top")
def get_leaderboard(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(
        Agent.avg_csat.desc(),
        Agent.tickets_solved.desc()
    ).limit(10).all()

    leaderboard = []
    for rank, agent in enumerate(agents, start=1):
        leaderboard.append({
            "rank"          : rank,
            "name"          : agent.name,
            "specialty"     : agent.specialty,
            "tickets_solved": agent.tickets_solved,
            "avg_csat"      : agent.avg_csat,
            "avg_speed_hrs" : agent.avg_speed_hrs
        })

    return {
        "leaderboard"  : leaderboard,
        "total_agents" : db.query(Agent).count()
    }