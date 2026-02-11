#!/usr/bin/env python3
"""
Customer Communication Assistant - Inbox Monitor & Triage (POC v2)

Monitors Agentmail inbox for new messages, performs AI triage,
and generates appropriate responses.

v2: Integrated improved OpenClaw-based triage system.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_triage import OpenClawTriage
from calendar_manager import CalendarManager

# Configuration
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
AGENTMAIL_EMAIL = os.getenv("AGENTMAIL_EMAIL")
AGENTMAIL_BASE_URL = "https://api.agentmail.to/v0"

class AgentmailClient:
    """Simple Agentmail API client"""
    
    def __init__(self, api_key: str, inbox_id: str):
        self.api_key = api_key
        self.inbox_id = inbox_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Fetch recent messages from inbox"""
        url = f"{AGENTMAIL_BASE_URL}/inboxes/{self.inbox_id}/messages"
        params = {"limit": limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("messages", [])
    
    def mark_as_read(self, message_id: str):
        """Mark message as read"""
        # Note: Check Agentmail API docs for actual endpoint
        # This is a placeholder
        pass
    
    def send_reply(self, to: str, subject: str, text: str, html: Optional[str] = None):
        """Send email reply"""
        url = f"{AGENTMAIL_BASE_URL}/inboxes/{self.inbox_id}/messages/send"
        
        payload = {
            "to": to,
            "subject": subject,
            "text": text
        }
        
        if html:
            payload["html"] = html
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            return None


class MessageTriage:
    """AI-powered message triage using OpenClaw integration"""
    
    def __init__(self):
        self.triage_engine = OpenClawTriage()
    
    def triage_message(self, message: Dict) -> Dict:
        """
        Perform AI triage on a message using OpenClaw's improved logic.
        """
        return self.triage_engine.triage_message(message)


class ActionRouter:
    """Routes triaged messages to appropriate actions"""
    
    def __init__(self, client: AgentmailClient, calendar: CalendarManager):
        self.client = client
        self.calendar = calendar
        self.send_emails_enabled = False  # Safety default
    
    def route(self, message: Dict, triage: Dict) -> str:
        """
        Decide and execute action based on triage result.
        Returns action taken (for logging).
        """
        
        intent = triage.get("intent")
        urgency = triage.get("urgency")
        
        if urgency == "emergency":
            return self._escalate_urgent(message, triage)
        elif intent == "booking":
            return self._handle_booking(message, triage)
        elif intent == "question":
            return self._handle_question(message, triage)
        elif intent == "complaint":
            return self._escalate_complaint(message, triage)
        elif intent == "spam":
            return self._mark_spam(message)
        else:
            return self._escalate_unknown(message, triage)
    
    def _escalate_urgent(self, message: Dict, triage: Dict) -> str:
        """Escalate urgent requests to human immediately"""
        print(f"🔴 URGENT ESCALATION: {triage.get('summary')}")
        
        # Send auto-reply acknowledging urgency
        sender = message.get("from", "unknown")
        subject = f"Re: {message.get('subject', 'Your urgent request')}"
        
        text = f"""Thank you for contacting us. We've received your urgent request.

We're escalating this to our team immediately and will contact you as soon as possible.

If you haven't already, please call us directly at: [BUSINESS_PHONE]

Summary of your request: {triage.get('summary')}

Best regards,
Customer Service Team"""
        
        if self.send_emails_enabled:
            result = self.client.send_reply(sender, subject, text)
            if result:
                print(f"   → ✅ Auto-reply sent to {sender} (message_id: {result.get('message_id', 'unknown')})")
            else:
                print(f"   → ❌ Failed to send auto-reply to {sender}")
        else:
            print(f"   → 📧 Would send auto-reply to {sender} (emails disabled)")
        print(f"   → TODO: Alert business owner via SMS/phone")
        
        return "escalated_urgent"
    
    def _handle_booking(self, message: Dict, triage: Dict) -> str:
        """Handle booking request with real calendar availability"""
        print(f"📅 BOOKING REQUEST: {triage.get('summary')}")
        
        sender = message.get("from", "unknown")
        service_type = triage.get("service_type", "service")
        urgency = triage.get("urgency", "flexible")
        
        # Get real available slots from calendar
        available_slots = self.calendar.get_next_available_slots(count=4, urgency=urgency)
        
        if not available_slots:
            print(f"   → No availability found for urgency: {urgency}")
            return "no_availability"
        
        # Format slots for customer
        formatted_slots = []
        for i, slot in enumerate(available_slots, 1):
            formatted = self.calendar.format_slot_for_customer(slot)
            formatted_slots.append(f"• Option {i}: {formatted}")
        
        slots_text = "\n".join(formatted_slots)
        
        text = f"""Thank you for your {service_type.replace('_', ' ')} request.

We have the following times available:

{slots_text}

Please reply with your preferred option number (1-{len(available_slots)}) and we'll get you scheduled right away.

For urgent matters, you can also call us directly at: [BUSINESS_PHONE]

Best regards,
Scheduling Team"""
        
        if self.send_emails_enabled:
            result = self.client.send_reply(sender, f"Re: {message.get('subject')}", text)
            if result:
                print(f"   → ✅ {len(available_slots)} availability options sent to {sender}")
            else:
                print(f"   → ❌ Failed to send availability options to {sender}")
        else:
            print(f"   → 📧 Would send {len(available_slots)} availability options to {sender} (emails disabled)")
        print(f"   → Slots offered: {', '.join([self.calendar.format_slot_for_customer(s) for s in available_slots])}")
        
        return "booking_options_sent"
    
    def _handle_question(self, message: Dict, triage: Dict) -> str:
        """Handle question - may need human review"""
        print(f"❓ QUESTION: {triage.get('summary')}")
        return "escalated_for_review"
    
    def _escalate_complaint(self, message: Dict, triage: Dict) -> str:
        """Escalate complaints to human"""
        print(f"⚠️  COMPLAINT: {triage.get('summary')}")
        return "escalated_complaint"
    
    def _mark_spam(self, message: Dict) -> str:
        """Mark as spam"""
        print(f"🚫 SPAM: {message.get('subject')}")
        return "marked_spam"
    
    def _escalate_unknown(self, message: Dict, triage: Dict) -> str:
        """Escalate unknown/unclear messages"""
        print(f"🤔 UNKNOWN: {triage.get('summary')}")
        return "escalated_unknown"


def main():
    """Main POC execution"""
    
    # Safety flag: set to True to actually send emails
    SEND_EMAILS = os.getenv("POC_SEND_EMAILS", "false").lower() == "true"
    
    print("=" * 60)
    print("Customer Communication Assistant - POC v3")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Send Emails: {'ENABLED' if SEND_EMAILS else 'DISABLED (set POC_SEND_EMAILS=true to enable)'}")
    print("=" * 60)
    print()
    
    # Initialize
    if not AGENTMAIL_API_KEY or not AGENTMAIL_EMAIL:
        print("❌ Error: AGENTMAIL_API_KEY and AGENTMAIL_EMAIL must be set")
        return 1
    
    client = AgentmailClient(AGENTMAIL_API_KEY, AGENTMAIL_EMAIL)
    triage_engine = MessageTriage()
    calendar = CalendarManager()
    router = ActionRouter(client, calendar)
    router.send_emails_enabled = SEND_EMAILS
    
    print(f"📧 Checking inbox: {AGENTMAIL_EMAIL}")
    print()
    
    # Fetch messages
    try:
        messages = client.get_messages(limit=5)
        print(f"Found {len(messages)} recent messages")
        print()
        
        if not messages:
            print("No messages to process.")
            return 0
        
        # Process each message
        for i, message in enumerate(messages, 1):
            print(f"Message {i}/{len(messages)}")
            print(f"From: {message.get('from', 'unknown')}")
            print(f"Subject: {message.get('subject', '(no subject)')}")
            print(f"Received: {message.get('created_at', 'unknown')}")
            print()
            
            # Triage
            triage = triage_engine.triage_message(message)
            print(f"Triage Result:")
            print(json.dumps(triage, indent=2))
            print()
            
            # Route action
            action = router.route(message, triage)
            print(f"Action Taken: {action}")
            print()
            print("-" * 60)
            print()
        
        print("✅ Processing complete")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
