from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

# ── Enums ──────────────────────────────────────────────
class TicketCategory(str, enum.Enum):
    payment = "payment"
    delivery = "delivery"
    quality = "quality"
    refund = "refund"
    no_response = "no_response"
    other = "other"

class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class UrgencyLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    critical = "critical"

# ── Tickets Table ───────────────────────────────────────
class Ticket(Base):
    __tablename__ = "tickets"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(String, nullable=False)         # from Bustler API
    project_id        = Column(String, nullable=True)          # auto-attached
    payment_status    = Column(String, nullable=True)          # auto-attached
    category          = Column(String, nullable=False)         # issue category
    description       = Column(Text, nullable=False)           # user's description
    status            = Column(String, default=TicketStatus.open)
    urgency           = Column(String, default=UrgencyLevel.low)
    is_anger_flagged  = Column(Integer, default=0)             # 1 = flagged
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    auto_reply_sent   = Column(Integer, default=0)             # 1 = auto reply was sent
    screenshot_url    = Column(String, nullable=True)   # uploaded image path
    created_at        = Column(DateTime, default=datetime.utcnow)
    resolved_at       = Column(DateTime, nullable=True)

    # relationships
    agent   = relationship("Agent", back_populates="tickets")
    report  = relationship("Report", back_populates="ticket", uselist=False)
    dispute = relationship("Dispute", back_populates="ticket", uselist=False)

# ── Agents Table ────────────────────────────────────────
class Agent(Base):
    __tablename__ = "agents"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    specialty     = Column(String, nullable=True)   # e.g. "payment", "quality"
    tickets_solved = Column(Integer, default=0)
    avg_csat      = Column(Integer, default=0)       # satisfaction score 1-5
    avg_speed_hrs = Column(Integer, default=0)       # average resolution time
    created_at    = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="agent")

# ── Disputes Table ──────────────────────────────────────
class Dispute(Base):
    __tablename__ = "disputes"

    id               = Column(Integer, primary_key=True, index=True)
    ticket_id        = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    raised_by        = Column(String, nullable=False)   # user_id who raised it
    against          = Column(String, nullable=False)   # user_id of other party
    evidence_url     = Column(Text, nullable=True)      # uploaded file path
    status           = Column(String, default="open")   # open / resolved
    resolution_notes = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="dispute")

# ── Reports Table ───────────────────────────────────────
class Report(Base):
    __tablename__ = "reports"

    id              = Column(Integer, primary_key=True, index=True)
    ticket_id       = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    category        = Column(String, nullable=False)    # copied from ticket
    what_broke      = Column(Text, nullable=False)      # auto or agent-filledcode
    why_it_happened = Column(Text, nullable=True)
    how_fixed       = Column(Text, nullable=True)
    csat_score      = Column(Integer, nullable=True)    # 1-5 from user survey
    created_at      = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="report")
# ── Users Table ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, unique=True, nullable=False)
    email      = Column(String, unique=True, nullable=False)
    password   = Column(String, nullable=False)  # hashed
    role       = Column(String, default="product_team")  # product_team / admin
    created_at = Column(DateTime, default=datetime.utcnow)