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
    "technical": "medium",
    "account": "medium",
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
    },
    "technical": {
        "keywords": [""],
        "reply": (
            "Hi! We've received your technical issue and our engineering "
            "team has been notified. We'll investigate and provide an "
            "update as soon as possible."
        )
    },
    "account": {
        "keywords": [""],
        "reply": (
            "Hi! We've received your account issue. Our support team "
            "will review your account and get back to you within "
            "24 hours to resolve this."
        )
    },
    "delivery": {
        "keywords": [""],
        "reply": (
            "Hi! We've received your delivery issue and it's been "
            "logged with our team. An agent will review the details "
            "and get back to you shortly."
        )
    },
    "quality": {
        "keywords": [""],
        "reply": (
            "Hi! Thanks for letting us know about the quality concern. "
            "Your ticket has been received and an agent will look into "
            "it and follow up with you soon."
        )
    },
    "other": {
        "keywords": [""],
        "reply": (
            "Hi! We've received your issue and it's been logged. "
            "Our team is looking into it and will follow up with you "
            "shortly."
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


# ── AI-Powered Triage (Gemini) ──────────────────────────
# Calls Gemini server-side to classify a ticket — free tier,
# no billing required. Falls back to keyword-based
# triage_ticket() if the API call fails for any reason —
# a ticket should never end up completely untriaged.

VALID_ROUTES = [
    "payment_team", "delivery_team", "quality_team",
    "refund_team", "no_response_team", "technical_team",
    "account_team", "ops_agent", "dispute_team"
]

def ai_triage_ticket(category: str, description: str) -> dict:
    try:
        from google import genai

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ AI triage skipped — GEMINI_API_KEY not configured, using keyword fallback")
            return triage_ticket(category, description)

        client = genai.Client(api_key=api_key)

        prompt = f"""You are a support ticket triage system for a freelance marketplace called Bustler.

Ticket category: {category}
Ticket description: {description}

Classify this ticket."""

        response_schema = {
            "type": "OBJECT",
            "properties": {
                "urgency": {
                    "type": "STRING",
                    "enum": ["low", "medium", "critical"]
                },
                "anger_detected": {"type": "BOOLEAN"},
                "route_to": {
                    "type": "STRING",
                    "enum": VALID_ROUTES
                },
                "auto_reply": {
                    "type": "STRING",
                    "description": "A short, empathetic 2-3 sentence reply to send the user. Empty string if no good auto-reply applies."
                },
                "auto_reply_sent": {"type": "BOOLEAN"}
            },
            "required": ["urgency", "anger_detected", "route_to", "auto_reply", "auto_reply_sent"]
        }

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
        )

        result = json.loads(response.text)

        return {
            "urgency": result.get("urgency", "low"),
            "is_anger_flagged": 1 if result.get("anger_detected") else 0,
            "route_to": result.get("route_to"),
            "auto_reply": result.get("auto_reply") or None,
            "auto_reply_sent": 1 if result.get("auto_reply_sent") else 0
        }

    except Exception as e:
        print(f"⚠️ AI triage failed, falling back to keyword triage: {e}")
        fallback = triage_ticket(category, description)
        fallback["route_to"] = None
        return fallback