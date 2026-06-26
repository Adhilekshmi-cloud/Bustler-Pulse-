import os
import json

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


# ── AI-Powered Triage (Claude) ──────────────────────────
# Calls Claude server-side to classify a ticket.
# Falls back to keyword-based triage_ticket() if the API
# call fails for any reason — a ticket should never end up
# completely untriaged.

VALID_ROUTES = [
    "payment_team", "delivery_team", "quality_team",
    "refund_team", "no_response_team", "ops_agent", "dispute_team"
]

def ai_triage_ticket(category: str, description: str) -> dict:
    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️ AI triage skipped — ANTHROPIC_API_KEY not configured, using keyword fallback")
            return triage_ticket(category, description)

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are a support ticket triage system for a freelance marketplace called Bustler.

Classify this ticket and respond with ONLY a JSON object, no other text, no markdown formatting.

Ticket category: {category}
Ticket description: {description}

Return JSON with exactly these fields:
- "urgency": one of "low", "medium", "critical"
- "anger_detected": true or false (true if the user sounds frustrated, angry, or threatening)
- "route_to": one of {VALID_ROUTES}
- "auto_reply": a short, empathetic 2-3 sentence reply to send the user, or null if no good auto-reply applies
- "auto_reply_sent": true if you provided an auto_reply, false otherwise

Respond with ONLY the JSON object."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        raw_text = response.content[0].text.strip()
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw_text)

        route_to = result.get("route_to")
        if route_to not in VALID_ROUTES:
            route_to = None

        return {
            "urgency": result.get("urgency", "low"),
            "is_anger_flagged": 1 if result.get("anger_detected") else 0,
            "route_to": route_to,
            "auto_reply": result.get("auto_reply"),
            "auto_reply_sent": 1 if result.get("auto_reply_sent") else 0
        }

    except Exception as e:
        print(f"⚠️ AI triage failed, falling back to keyword triage: {e}")
        fallback = triage_ticket(category, description)
        fallback["route_to"] = None
        return fallback