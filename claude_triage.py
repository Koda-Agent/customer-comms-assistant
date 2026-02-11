#!/usr/bin/env python3
"""
Claude API integration for intelligent message triage.
Uses Anthropic's Claude API to analyze customer messages and extract structured intent.
"""

import os
import json
from typing import Dict, Optional
import anthropic

class ClaudeTriage:
    """Claude-powered message triage for customer communication"""
    
    SYSTEM_PROMPT = """You are an AI assistant that triages customer service messages for home service businesses (HVAC, plumbing, electrical, cleaning, landscaping).

Your job is to analyze incoming customer messages and extract structured information to help route them appropriately.

Always respond with valid JSON only, no other text."""

    TRIAGE_PROMPT_TEMPLATE = """Analyze this customer message and extract structured information:

FROM: {sender}
SUBJECT: {subject}
MESSAGE:
{body}

Extract and return ONLY valid JSON with these fields:
{{
  "intent": "booking|question|complaint|urgent|spam|other",
  "service_type": "hvac_repair|hvac_maintenance|plumbing_repair|plumbing_maintenance|electrical_repair|electrical_maintenance|cleaning|landscaping|other",
  "urgency": "emergency|today|this_week|flexible|unknown",
  "preferred_times": ["list of any mentioned time preferences as strings"],
  "customer_name": "name if mentioned, else null",
  "customer_phone": "phone if mentioned, else null",
  "customer_address": "address if mentioned, else null",
  "confidence": "high|medium|low - your confidence in this classification",
  "summary": "1-2 sentence summary of the request",
  "reasoning": "brief explanation of why you chose this classification"
}}

Guidelines:
- intent "urgent": Use for emergencies, ASAP requests, or situations causing immediate problems
- intent "booking": Customer wants to schedule service
- intent "question": Asking about pricing, availability, or general info
- intent "complaint": Expressing dissatisfaction or problems with service
- urgency "emergency": Immediate danger or critical failure (no heat in winter, flooding, etc)
- urgency "today": Wants service today but not critical
- If unsure, mark confidence as "low" and escalate via intent "other"
- For spam/marketing emails, mark as "spam"

Respond ONLY with the JSON object, no markdown formatting."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or passed to constructor")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def triage_message(self, message: Dict) -> Dict:
        """
        Analyze a message and extract structured triage information.
        
        Args:
            message: Dict with keys: from, subject, body/preview
            
        Returns:
            Dict with triage fields (intent, service_type, urgency, etc)
        """
        # Extract message fields
        sender = message.get("from", "Unknown")
        subject = message.get("subject", "(no subject)")
        body = message.get("text") or message.get("preview", "")
        
        # Build prompt
        prompt = self.TRIAGE_PROMPT_TEMPLATE.format(
            sender=sender,
            subject=subject,
            body=body[:2000]  # Truncate very long messages
        )
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
                max_tokens=1024,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text.strip()
            
            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            triage_result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["intent", "service_type", "urgency", "summary"]
            for field in required_fields:
                if field not in triage_result:
                    triage_result[field] = "unknown"
            
            return triage_result
            
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse Claude response as JSON: {e}")
            print(f"Response was: {response_text[:200]}")
            
            # Fallback to basic extraction
            return {
                "intent": "other",
                "service_type": "other",
                "urgency": "unknown",
                "confidence": "low",
                "summary": subject[:100],
                "reasoning": f"JSON parse error: {str(e)}",
                "preferred_times": [],
                "customer_name": None,
                "customer_phone": None,
                "customer_address": None
            }
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # Return fallback result
            return {
                "intent": "other",
                "service_type": "other",
                "urgency": "unknown",
                "confidence": "low",
                "summary": subject[:100],
                "reasoning": f"API error: {str(e)}",
                "preferred_times": [],
                "customer_name": None,
                "customer_phone": None,
                "customer_address": None
            }


def test_triage():
    """Test the Claude triage system with sample messages"""
    
    # Sample test messages
    test_messages = [
        {
            "from": "john.smith@email.com",
            "subject": "AC not working - need help today!",
            "text": "Hi, my air conditioner stopped working this morning and it's supposed to be 95 degrees today. Can someone come out as soon as possible? I'm at 123 Main Street. Thanks!"
        },
        {
            "from": "jane.doe@email.com",
            "subject": "Question about maintenance plans",
            "text": "Hi, I saw on your website you offer annual maintenance plans. How much do they cost and what's included? Also, do you service both heating and cooling systems?"
        },
        {
            "from": "bob.jones@email.com",
            "subject": "Very disappointed",
            "text": "I scheduled an appointment for today between 2-4pm and nobody showed up. I took time off work for this. Please call me to explain what happened."
        }
    ]
    
    print("Testing Claude Triage System")
    print("=" * 60)
    print()
    
    triage = ClaudeTriage()
    
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
    # Run tests if executed directly
    test_triage()
