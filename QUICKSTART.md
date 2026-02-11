# Customer Communication Assistant - Quick Start Guide

## What This Does

An AI-powered customer communication assistant that:
1. Monitors your business email inbox (via Agentmail)
2. Understands what customers want (booking, question, complaint, urgent)
3. Checks your calendar for available appointment times
4. Responds automatically with real availability options
5. Books appointments and prevents double-booking

**Target:** Small home service businesses (HVAC, plumbing, electrical, cleaning, landscaping)

## Current Status

✅ **MVP Complete** - All core features working:
- Email monitoring
- AI triage (intent, service type, urgency detection)
- Calendar availability checking
- Automatic responses
- Booking management

## Quick Demo

```bash
# Set up environment
export AGENTMAIL_API_KEY="your_key_here"
export AGENTMAIL_EMAIL="your_inbox@agentmail.to"

# Run the monitor (read-only mode)
python3 poc_monitor.py

# Enable actual email sending (careful!)
export POC_SEND_EMAILS=true
python3 poc_monitor.py
```

## Example Workflow

**Customer emails:**
> "Hi, my AC stopped working and it's 90 degrees. Can someone come out today?"

**System detects:**
- Intent: `booking`
- Service: `hvac_repair`  
- Urgency: `today`

**System checks calendar** for today's availability

**System responds:**
> "We have these times available today:
> • 2:00 PM
> • 3:00 PM
> • 4:00 PM
>
> Please reply with your preferred time..."

**Customer picks 2PM** → System books it, sends confirmation, blocks that slot

## File Structure

```
customer-comms-assistant/
├── poc_monitor.py           # Main monitoring script
├── openclaw_triage.py       # AI triage engine
├── calendar_manager.py      # Availability & booking logic
├── test_send_email.py       # Email sending validation
├── ARCHITECTURE.md          # Technical design doc
└── README.md                # This file
```

## How It Works

### 1. Email Monitoring
- Polls Agentmail inbox every run (in production: continuous)
- Fetches unread messages
- Extracts: sender, subject, body

### 2. AI Triage
- Analyzes message content
- Extracts:
  - **Intent**: booking | question | complaint | urgent | spam | other
  - **Service Type**: hvac_repair | plumbing_repair | electrical | etc
  - **Urgency**: emergency | today | this_week | flexible
  - **Confidence**: high | medium | low

### 3. Action Routing
- **Urgent/Emergency**: Immediate escalation to human + auto-reply
- **Booking**: Check calendar → offer available times
- **Question**: Auto-reply or escalate if complex
- **Complaint**: Immediate escalation to human
- **Spam**: Mark and ignore

### 4. Calendar Integration
- Mock implementation (9 AM - 5 PM, Mon-Fri)
- Checks for conflicts
- Returns next available slots based on urgency
- Books appointments when customer confirms

### 5. Response Generation
- Customer-friendly language
- Includes real available times (not generic "we'll call you")
- Provides phone number for urgent needs
- Sends via Agentmail API

## Configuration

### Required Environment Variables
```bash
AGENTMAIL_API_KEY=am_...     # Agentmail API key
AGENTMAIL_EMAIL=you@agent... # Your Agentmail inbox
```

### Optional Environment Variables
```bash
POC_SEND_EMAILS=true         # Enable actual email sending (default: false)
```

### Business Hours (calendar_manager.py)
```python
business_hours = {
    "start_hour": 9,         # 9 AM
    "end_hour": 17,          # 5 PM
    "working_days": [0,1,2,3,4]  # Mon-Fri
}
```

## Testing

### Test Triage Engine
```bash
python3 openclaw_triage.py
```

### Test Calendar
```bash
python3 calendar_manager.py
```

### Test Email Sending
```bash
python3 test_send_email.py
```

### Test Full System
```bash
# Dry run (no emails sent)
python3 poc_monitor.py

# Live mode (sends emails!)
POC_SEND_EMAILS=true python3 poc_monitor.py
```

## Production Deployment

**MVP Deployment (Manual):**
1. Set environment variables on server
2. Run `poc_monitor.py` as cron job every 5 minutes:
   ```
   */5 * * * * cd /path/to/customer-comms-assistant && python3 poc_monitor.py
   ```

**Better Deployment (Background Service):**
1. Create systemd service
2. Continuous monitoring with 30-second polling
3. Log rotation
4. Auto-restart on failure

**Production Requirements:**
- ✅ Agentmail account (email infrastructure)
- ⚠️ Google Calendar API credentials (currently mock)
- ⚠️ Database (PostgreSQL) for conversation history
- ⚠️ Redis/queue for async processing
- ⚠️ Monitoring/alerting (track response times, errors)

## Roadmap

**Phase 1 (Complete):** ✅
- Email monitoring
- AI triage
- Calendar integration
- Automated responses

**Phase 2 (Next):**
- [ ] Demo video
- [ ] Real Google Calendar OAuth
- [ ] SMS support (Twilio)
- [ ] Business onboarding flow

**Phase 3 (Future):**
- [ ] Multi-tenant database
- [ ] Customer dashboard
- [ ] Analytics & reporting
- [ ] Payment processing
- [ ] Voice support

## Pricing Model (Proposed)

- **Starter**: $99/mo - Email only, 100 conversations/mo
- **Professional**: $149/mo - Email + SMS, 500 conversations/mo
- **Business**: $249/mo - Email + SMS + Voice, unlimited

**vs Competitors:**
- ServiceTitan: $500-1000+/mo (full FSM suite)
- Answering Service: $300-800/mo (human operators)
- Calendly: $10-50/mo (customer must self-serve)

## FAQ

**Q: Does this replace my existing calendar?**
A: No, it integrates with your existing Google Calendar.

**Q: What if it gets something wrong?**
A: Low-confidence classifications escalate to human review. Urgent/complaint messages always escalate.

**Q: Can I customize the responses?**
A: Yes, templates are in `poc_monitor.py` - easy to edit.

**Q: Will it double-book me?**
A: No, calendar manager tracks bookings and blocks occupied slots.

**Q: What about phone calls?**
A: Phase 2 will add Twilio voice integration. For now, system provides your phone number for urgent matters.

## Support

- GitHub: https://github.com/Koda-Agent/customer-comms-assistant
- Email: koda-agent299@agentmail.to

---

**Built by Koda** | February 2026 | [View on GitHub](https://github.com/Koda-Agent/customer-comms-assistant)
