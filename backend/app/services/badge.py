from sqlalchemy.orm import Session
from app.models import Ticket
from datetime import datetime

# ── Badge Service ────────────────────────────────────────
# Called automatically when a ticket is resolved
# Writes "Supported by Bustler" badge info to the ticket
# This data is sent back to Bustler's API to show on profile

# ── Badge Messages by Category ───────────────────────────
BADGE_MESSAGES = {
    "payment"    : "Payment issue resolved with Bustler's support",
    "refund"     : "Refund successfully processed via Bustler support",
    "delivery"   : "Delivery dispute resolved by Bustler's ops team",
    "quality"    : "Quality concern addressed by Bustler's ops team",
    "no_response": "Communication issue resolved via Bustler support",
    "other"      : "Issue resolved with support from Bustler's team"
}

# ── Badge Levels ─────────────────────────────────────────
# Users get a higher badge tier the more issues they resolve
# Encourages trust and shows platform reliability

def get_badge_level(tickets_resolved: int) -> str:
    if tickets_resolved >= 10:
        return "Platinum"
    elif tickets_resolved >= 5:
        return "Gold"
    elif tickets_resolved >= 2:
        return "Silver"
    else:
        return "Bronze"


# ── Main Badge Function ───────────────────────────────────
def award_badge(
    db: Session,
    ticket: Ticket,
) -> dict:
    """
    Called inside PATCH /ticket/resolve.
    Returns badge data to be sent back to Bustler's API.
    In a real integration this would call Bustler's
    PATCH /user/{user_id}/badge endpoint.
    """

    # Count how many tickets this user has had resolved
    resolved_count = (
        db.query(Ticket)
        .filter(
            Ticket.user_id == ticket.user_id,
            Ticket.status == "resolved"
        )
        .count()
    )

    badge_level   = get_badge_level(resolved_count + 1)
    badge_message = BADGE_MESSAGES.get(ticket.category, BADGE_MESSAGES["other"])

    badge_data = {
        "user_id"      : ticket.user_id,
        "badge_level"  : badge_level,
        "badge_message": badge_message,
        "awarded_at"   : datetime.utcnow().isoformat(),
        "ticket_id"    : ticket.id
    }

    # TODO: when Bustler shares their API key, call their endpoint here:
    # requests.patch(f"{BUSTLER_API}/user/{ticket.user_id}/badge", json=badge_data)

    return badge_data