# ── Triage Engine ───────────────────────────────────────
# Reads every ticket and automatically:
# 1. Scores urgency (low / medium / critical)
# 2. Detects anger in the description
# 3. Suggests the best agent based on category
# 4. Checks if it's a known repeat issue for auto-reply

# ── Anger Keywords ──────────────────────────────────────
ANGER_KEYWORDS = [
    "fraud", "scam", "cheated", "useless", "worst",
    "terrible", "disgusting", "pathetic", "ridiculous",
    "unacceptable", "furious", "angry", "lawsuit",
    "refund immediately", "waste", "horrible", "never again"
]

# ── Urgency Rules by Category ───────────────────────────
URGENCY_MAP = {
    "payment": "critical",
    "refund": "critical",
    "no_response": "medium",
    "delivery": "medium",
    "quality": "low",
    "other": "low"
}

# ── Known Issues for Auto-Reply ─────────────────────────
KNOWN_ISSUES = {
    "payment": {
        "keywords": ["delay", "not received", "pending", "failed"],
        "reply": (
            "Hi! We understand your concern about the payment. "
            "Payments typically reflect within 3-5 business days. "
            "If it has been longer, please raise a dispute and our "
            "team will prioritize it immediately."
        )
    },
    "refund": {
        "keywords": ["when", "status", "not received", "delay"],
        "reply": (
            "Hi! Refunds are processed within 5-7 business days "
            "after approval. Your refund is being tracked and you "
            "will receive an email once it is credited."
        )
    },
    "no_response": {
        "keywords": ["not responding", "no reply", "ignoring", "silent"],
        "reply": (
            "Hi! We are sorry to hear that. We have flagged this "
            "freelancer's account and an ops agent will follow up "
            "within 24 hours to help resolve this."
        )
    }
}

# ── Main Triage Function ────────────────────────────────
def triage_ticket(category: str, description: str) -> dict:
    description_lower = description.lower()

    # 1. Score urgency
    urgency = URGENCY_MAP.get(category, "low")

    # 2. Detect anger — upgrade urgency to critical if angry
    is_anger_flagged = 0
    for keyword in ANGER_KEYWORDS:
        if keyword in description_lower:
            is_anger_flagged = 1
            urgency = "critical"  # always critical if user is angry
            break

    # 3. Check for known issue → auto-reply
    auto_reply = None
    auto_reply_sent = 0

    if category in KNOWN_ISSUES:
        known = KNOWN_ISSUES[category]
        for kw in known["keywords"]:
            if kw in description_lower:
                auto_reply = known["reply"]
                auto_reply_sent = 1
                break

    # 4. Return triage result
    return {
        "urgency": urgency,
        "is_anger_flagged": is_anger_flagged,
        "auto_reply": auto_reply,
        "auto_reply_sent": auto_reply_sent
    }


# ── Agent Suggestion ────────────────────────────────────
def suggest_agent(category: str, agents: list) -> object:
    """
    From the list of available agents, pick the best one:
    - First preference: agent whose specialty matches the category
    - Second preference: agent with highest CSAT score
    - Fallback: first available agent
    """
    if not agents:
        return None

    # Try to find specialty match
    specialty_match = [a for a in agents if a.specialty == category]
    if specialty_match:
        # Among specialty matches, pick highest CSAT
        return max(specialty_match, key=lambda a: a.avg_csat)

    # No specialty match — pick highest CSAT overall
    return max(agents, key=lambda a: a.avg_csat)