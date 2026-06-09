from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── Agent Schemas ───────────────────────────────────────
class AgentBase(BaseModel):
    name: str
    email: str
    specialty: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentResponse(AgentBase):
    id: int
    tickets_solved: int
    avg_csat: int
    avg_speed_hrs: int
    created_at: datetime

    class Config:
        from_attributes = True

# ── Ticket Schemas ──────────────────────────────────────
class TicketCreate(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    payment_status: Optional[str] = None
    category: str
    description: str

class TicketResolve(BaseModel):
    resolution_notes: str
    what_broke: str
    why_it_happened: Optional[str] = None
    how_fixed: Optional[str] = None
    csat_score: Optional[int] = None

class TicketResponse(BaseModel):
    id: int
    user_id: str
    project_id: Optional[str]
    payment_status: Optional[str]
    category: str
    description: str
    status: str
    urgency: str
    is_anger_flagged: int
    auto_reply_sent: int
    assigned_agent_id: Optional[int]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

# ── Dispute Schemas ─────────────────────────────────────
class DisputeCreate(BaseModel):
    ticket_id: int
    raised_by: str
    against: str
    evidence_url: Optional[str] = None

class DisputeResponse(DisputeCreate):
    id: int
    status: str
    resolution_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ── Report Schemas ──────────────────────────────────────
class ReportResponse(BaseModel):
    id: int
    ticket_id: int
    category: str
    what_broke: str
    why_it_happened: Optional[str]
    how_fixed: Optional[str]
    csat_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# ── Health Schema ───────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    open_tickets: int
    critical_tickets: int
    resolved_today: int
    message: str
# ── Auth Schemas ────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "product_team"

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str    