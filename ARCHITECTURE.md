# Technical Architecture - Customer Communication Assistant

## System Overview

```
┌─────────────────┐
│  Customer       │
│  Channels       │
│  (Email/SMS)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Inbox Monitor  │
│  (Agentmail)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  AI Triage      │
│  (OpenClaw)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Action Router  │
│  - Book appt    │
│  - Send confirm │
│  - Escalate     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Integrations   │
│  - Calendar     │
│  - SMS/Email    │
│  - Business CRM │
└─────────────────┘
```

## Component Design

### 1. Inbox Monitor
**Purpose**: Poll customer communication channels for new messages
**Technology**: Agentmail API, potential Twilio for SMS
**Frequency**: Every 5 minutes (configurable)
**Output**: New message events with metadata

**Implementation**:
```python
# Pseudo-code
def check_inbox():
    messages = agentmail.get_unread()
    for msg in messages:
        event = {
            'id': msg.id,
            'from': msg.sender,
            'subject': msg.subject,
            'body': msg.text,
            'channel': 'email',
            'timestamp': msg.received_at
        }
        queue_for_processing(event)
```

### 2. AI Triage Engine
**Purpose**: Analyze incoming messages and extract structured data
**Technology**: Claude via OpenClaw
**Input**: Raw message content
**Output**: Structured intent + extracted data

**Extraction Fields**:
- `intent`: booking | question | complaint | urgent | spam
- `service_type`: hvac_repair | hvac_maintenance | plumbing | etc.
- `urgency`: emergency | today | this_week | flexible
- `preferred_times`: [datetime objects]
- `customer_info`: {name, phone, address}
- `additional_context`: free text summary

**Example**:
```
Input: "Hi, my AC stopped working and it's 95 degrees. Can someone come today?"

Output: {
  "intent": "booking",
  "service_type": "hvac_repair",
  "urgency": "emergency",
  "preferred_times": ["today"],
  "customer_info": {
    "name": null,  // not in message
    "phone": null,
    "address": null
  },
  "additional_context": "AC not working, 95 degree heat"
}
```

### 3. Action Router
**Purpose**: Decide what action to take based on triage output
**Technology**: Python logic + integrations

**Decision Tree**:
```
if urgency == "emergency":
    → escalate_to_human(priority=high)
elif intent == "booking":
    → check_calendar_availability()
    → send_booking_options()
elif intent == "question":
    → generate_response() or escalate_if_complex()
elif intent == "spam":
    → mark_as_spam()
else:
    → escalate_to_human(priority=normal)
```

### 4. Calendar Integration
**Purpose**: Check availability and book appointments
**Technology**: Google Calendar API (MVP), extensible to others

**Operations**:
- `get_availability(date_range)` → list of open slots
- `book_appointment(slot, customer, service_type)` → confirmation
- `send_confirmation(customer, appointment)` → email/SMS

### 5. Response Generator
**Purpose**: Send automated responses back to customer
**Technology**: Agentmail (email), Twilio (SMS)

**Message Templates**:
- Appointment confirmation
- Availability options
- Can't help / escalation notice
- Follow-up reminders

## Data Storage

### Database Schema (PostgreSQL)

```sql
-- Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_name VARCHAR(255),
    status VARCHAR(50), -- active, resolved, escalated
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    direction VARCHAR(10), -- inbound, outbound
    channel VARCHAR(20), -- email, sms, voice
    content TEXT,
    intent VARCHAR(50),
    urgency VARCHAR(20),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    service_type VARCHAR(100),
    scheduled_at TIMESTAMP,
    duration_minutes INTEGER,
    status VARCHAR(50), -- pending, confirmed, completed, cancelled
    calendar_event_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Businesses (for multi-tenant)
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    calendar_id VARCHAR(255), -- Google Calendar ID
    config JSONB, -- business-specific settings
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Considerations

1. **API Key Storage**: All keys in `/home/ubuntu/.openclaw/.env` with 600 permissions
2. **Customer Data**: Encrypted at rest, minimal retention (30 days)
3. **Access Control**: Multi-tenant isolation via business_id
4. **Audit Log**: All AI decisions logged for review

## Deployment Architecture (MVP)

**Phase 1 (POC)**: Single script, local execution
- Runs on current OpenClaw host
- Manual trigger / cron job
- Logs to file

**Phase 2 (MVP)**: Background service
- Systemd service on OpenClaw host
- Continuous polling
- Database-backed state

**Phase 3 (Production)**: Scalable microservices
- Inbox monitor (separate service)
- Triage worker pool
- API gateway for business management
- Consider: AWS Lambda, Docker, or dedicated VPS

## Performance Requirements

- **Response Time**: < 5 minutes from message receipt to first response
- **Availability**: 99% uptime (monitor with heartbeat)
- **Throughput**: MVP handles 1-5 businesses, 50-200 messages/day
- **Cost**: Stay under $0.10 per interaction

## Testing Strategy

1. **Unit Tests**: Each component in isolation
2. **Integration Tests**: End-to-end message flow
3. **Manual Testing**: Real email/SMS with mock business
4. **Pilot Testing**: 1-2 friendly businesses (free trial)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI misunderstands urgent request | High | Always escalate unclear urgency |
| Calendar double-booking | Medium | Implement locking mechanism |
| API rate limits exceeded | Medium | Queue system + backoff |
| Customer data breach | High | Encryption + minimal retention |
| Cost overruns on APIs | Medium | Per-message budget caps |

## Next Implementation Steps

1. Set up PostgreSQL database (use postgres skill)
2. Create Agentmail inbox monitoring script
3. Build AI triage prompt template
4. Implement action router logic
5. Test with mock data end-to-end
6. Deploy as cron job for continuous operation

---

**Document Version**: 0.1
**Last Updated**: 2026-02-11
**Status**: Draft for POC
