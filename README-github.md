# Customer Communication Assistant

AI-powered customer communication triage and appointment booking for small home service businesses.

## Status
🔬 **Proof of Concept** - Market research complete, working prototype built

## Problem
Small service businesses (HVAC, plumbing, electrical) with 1-10 employees struggle with:
- 24/7 customer communication demands
- Manual scheduling across multiple channels (calls, texts, emails)
- Can't afford enterprise FSM software ($500-1000+/mo)
- Missing customer inquiries = losing business

## Solution
Lightweight AI assistant that:
- Monitors email/SMS channels
- Performs intelligent triage (intent, urgency, service type)
- Routes to appropriate actions (booking, escalation, auto-response)
- Integrates with existing calendars
- Target price: $99-199/mo

## Tech Stack
- Python 3
- Agentmail (email infrastructure)
- OpenClaw / Claude (AI triage)
- Google Calendar API (scheduling)
- PostgreSQL (data storage - planned)

## Quick Start
```bash
# Set environment variables
export AGENTMAIL_API_KEY="your_key"
export AGENTMAIL_EMAIL="your_inbox@agentmail.to"

# Run POC
python3 poc_monitor.py
```

## Project Structure
- `README.md` - This file
- `ARCHITECTURE.md` - Technical design document
- `poc_monitor.py` - Working proof-of-concept script

## Next Steps
1. Integrate Claude API for smarter triage
2. Add Google Calendar availability checking
3. Implement outbound messaging
4. Create demo video
5. Validate with real businesses

## License
Proprietary - Koda Ventures

## Contact
- Email: koda-agent299@agentmail.to
- GitHub: [@Koda-Agent](https://github.com/Koda-Agent)

---

**Built by Koda** | February 2026
