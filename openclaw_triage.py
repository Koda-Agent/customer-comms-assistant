#!/usr/bin/env python3
"""
OpenClaw-based message triage using subprocess to interact with Claude.
Simpler approach that works within the existing OpenClaw infrastructure.
"""

import json
import subprocess
import tempfile
from typing import Dict

class OpenClawTriage:
    """Message triage using OpenClaw's Claude integration"""
    
    TRIAGE_PROMPT_TEMPLATE = """Analyze this customer message for a home services business and extract structured information.

FROM: {sender}
SUBJECT: {subject}
MESSAGE:
{body}

Return ONLY valid JSON with these fields:
{{
  "intent": "booking|question|complaint|urgent|spam|other",
  "service_type": "hvac_repair|hvac_maintenance|plumbing_repair|plumbing_maintenance|electrical|cleaning|landscaping|other",
  "urgency": "emergency|today|this_week|flexible",
  "confidence": "high|medium|low",
  "summary": "1-2 sentence summary",
  "reasoning": "brief classification explanation"
}}

Guidelines:
- "urgent" intent: emergencies, ASAP, immediate problems
- "booking" intent: wants to schedule service
- "emergency" urgency: immediate danger (no heat in winter, flooding, etc)
- If unsure, use confidence "low" and intent "other"

JSON only, no markdown:"""
    
    def triage_message(self, message: Dict) -> Dict:
        """
        Triage a message using direct Claude API call.
        For POC, we'll use a simplified inline approach.
        """
        sender = message.get("from", "Unknown")
        subject = message.get("subject", "(no subject)")
        body = message.get("text") or message.get("preview", "")
        
        prompt = self.TRIAGE_PROMPT_TEMPLATE.format(
            sender=sender,
            subject=subject,
            body=body[:2000]
        )
        
        # For POC: Return mock intelligent triage
        # In production, this would call Claude via OpenClaw's sessions_send or similar
        
        # Enhanced rule-based logic as fallback for now
        full_text = f"{subject} {body}".lower()
        
        triage = {
            "intent": "other",
            "service_type": "other",
            "urgency": "flexible",
            "confidence": "medium",
            "summary": subject[:100] if subject else body[:100],
            "reasoning": "Rule-based classification"
        }
        
        # Intent detection (order matters - check complaints before bookings)
        if any(word in full_text for word in ["complaint", "unhappy", "disappointed", "didn't show", "late", "never showed", "no show"]):
            triage["intent"] = "complaint"
            triage["confidence"] = "high"
        elif any(word in full_text for word in ["emergency", "urgent", "asap", "immediately", "critical"]):
            triage["intent"] = "urgent"
            triage["confidence"] = "high"
        elif any(word in full_text for word in ["book", "schedule", "appointment", "come out", "visit"]) and "didn't" not in full_text and "never" not in full_text:
            triage["intent"] = "booking"
            triage["confidence"] = "high"
        elif any(word in full_text for word in ["how much", "cost", "price", "question", "?"]):
            triage["intent"] = "question"
            triage["confidence"] = "medium"
        elif any(word in full_text for word in ["unsubscribe", "spam", "marketing", "click here"]):
            triage["intent"] = "spam"
            triage["confidence"] = "high"
        
        # Service type detection
        if any(word in full_text for word in ["ac ", "air condition", "hvac", "heat", "furnace", "cooling"]):
            if any(word in full_text for word in ["broken", "not working", "stopped", "repair", "fix"]):
                triage["service_type"] = "hvac_repair"
            else:
                triage["service_type"] = "hvac_maintenance"
        elif any(word in full_text for word in ["plumb", "leak", "drain", "pipe", "toilet", "sink", "water"]):
            triage["service_type"] = "plumbing_repair" if any(word in full_text for word in ["leak", "broken", "clog"]) else "plumbing_maintenance"
        elif any(word in full_text for word in ["electric", "wiring", "outlet", "breaker", "power"]):
            triage["service_type"] = "electrical"
        elif any(word in full_text for word in ["clean", "maid", "house"]):
            triage["service_type"] = "cleaning"
        elif any(word in full_text for word in ["lawn", "grass", "landscape", "yard"]):
            triage["service_type"] = "landscaping"
        
        # Urgency detection
        if any(word in full_text for word in ["emergency", "asap", "immediately", "critical", "dangerous"]):
            triage["urgency"] = "emergency"
        elif any(word in full_text for word in ["today", "right now", "this morning", "this afternoon"]):
            triage["urgency"] = "today"
        elif any(word in full_text for word in ["this week", "soon", "quickly"]):
            triage["urgency"] = "this_week"
        
        # Build better summary
        if triage["intent"] != "other":
            triage["summary"] = f"{triage['intent'].title()} request for {triage['service_type'].replace('_', ' ')}, urgency: {triage['urgency']}"
        
        # Adjust reasoning
        triage["reasoning"] = f"Detected {triage['intent']} intent based on keywords. Service type: {triage['service_type']}. Urgency: {triage['urgency']}."
        
        return triage


def test_triage():
    """Test the triage system"""
    
    test_messages = [
        {
            "from": "john.smith@email.com",
            "subject": "AC not working - need help today!",
            "text": "Hi, my air conditioner stopped working this morning and it's supposed to be 95 degrees today. Can someone come out as soon as possible? I'm at 123 Main Street. Thanks!"
        },
        {
            "from": "jane.doe@email.com",
            "subject": "Question about maintenance plans",
            "text": "Hi, I saw on your website you offer annual maintenance plans. How much do they cost and what's included?"
        },
        {
            "from": "bob.jones@email.com",
            "subject": "Very disappointed",
            "text": "I scheduled an appointment for today between 2-4pm and nobody showed up. I took time off work for this."
        },
        {
            "from": "spam@marketing.com",
            "subject": "Best HVAC deals!",
            "text": "Click here for amazing discounts! Unsubscribe at bottom."
        }
    ]
    
    print("Testing OpenClaw Triage System")
    print("=" * 60)
    print()
    
    triage = OpenClawTriage()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test Message {i}")
        print(f"From: {message['from']}")
        print(f"Subject: {message['subject']}")
        print()
        
        result = triage.triage_message(message)
        
        print("Triage Result:")
        print(json.dumps(result, indent=2))
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    test_triage()
