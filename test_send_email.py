#!/usr/bin/env python3
"""
Test script to validate Agentmail sending functionality.
Sends a test email to verify the API integration works.
"""

import os
import sys
import requests

AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
AGENTMAIL_EMAIL = os.getenv("AGENTMAIL_EMAIL")
AGENTMAIL_BASE_URL = "https://api.agentmail.to/v0"

def test_send():
    """Test sending an email via Agentmail"""
    
    if not AGENTMAIL_API_KEY or not AGENTMAIL_EMAIL:
        print("Error: AGENTMAIL_API_KEY and AGENTMAIL_EMAIL must be set")
        return 1
    
    url = f"{AGENTMAIL_BASE_URL}/inboxes/{AGENTMAIL_EMAIL}/messages/send"
    
    headers = {
        "Authorization": f"Bearer {AGENTMAIL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Send test email to ourselves
    payload = {
        "to": AGENTMAIL_EMAIL,
        "subject": "Test from POC Monitor - Outbound Email",
        "text": "This is a test email from the customer communication assistant POC.\n\nIf you receive this, outbound email is working correctly!"
    }
    
    print("Sending test email...")
    print(f"From: {AGENTMAIL_EMAIL}")
    print(f"To: {AGENTMAIL_EMAIL}")
    print(f"Subject: {payload['subject']}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Email sent successfully!")
        print(f"Response: {result}")
        return 0
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending email: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
        return 1


if __name__ == "__main__":
    exit(test_send())
