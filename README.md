# Customer Communication Assistant

**Status**: Market research & validation phase
**Target Market**: Small home service businesses (1-10 employees)
**Value Prop**: AI-powered customer communication triage and appointment booking

## Problem Statement

Small service businesses (HVAC, plumbing, electrical, cleaning, landscaping) are drowning in customer communication across multiple channels (calls, texts, emails, social). They can't afford enterprise field service management software ($500-1000/mo) or traditional answering services ($300-800/mo), but missing calls means losing customers in competitive markets.

## Solution Hypothesis

An AI communication assistant that:
- Monitors email, SMS, and potentially voice channels
- Performs first-line triage (what, when, urgency)
- Books appointments into existing calendars
- Sends confirmations and reminders
- Escalates complex/urgent issues to humans

**Target Price**: $99-199/month

## Market Research Summary

### Validated Pain Points
- 24/7 availability requirement (after-hours, weekends, holidays)
- High volume of repetitive scheduling requests
- Manual processes still dominant (spreadsheets, disconnected tools)
- Slow response time = lost customers
- Labor shortages driving automation need

### Competitor Landscape
- **High-end FSM**: ServiceTitan, FIELDBOSS, Jobber ($300-1000+/mo) - Full suite, complex
- **Answering Services**: PATLive, AnswerFirst ($300-800/mo) - Human operators, established
- **DIY Tools**: Calendly, Acuity Scheduling ($10-50/mo) - Customer must self-serve

### Our Differentiation
- Lower price than FSM or answering services
- More intelligent than self-serve booking tools
- Integrates with existing tools (not a replacement)
- Fast setup (days not months)

## Technical Stack (Proposed)

- **Inbox monitoring**: Agentmail (email), Twilio (SMS), potentially voice
- **AI engine**: OpenClaw / Claude
- **Calendar integration**: Google Calendar API, potentially Calendly API
- **Database**: PostgreSQL (via existing skills)
- **Hosting**: Current AWS infrastructure

## Next Actions

1. Build proof-of-concept
   - Email monitoring + simple triage
   - Mock appointment booking flow
   - Demo-ready in 3-5 days

2. Validation loop
   - Create demo video
   - Reach out to 10-20 target businesses
   - Iterate based on feedback

3. MVP features (post-validation)
   - Multi-channel monitoring
   - Calendar integration
   - Automated responses
   - Human escalation system

## Success Criteria

**Phase 1 (Research)**: ✅ Completed
- Identify 3-5 target business types: ✅ HVAC, plumbing, electrical, cleaning, landscaping
- Validate pain points: ✅ After-hours availability, scheduling chaos, manual processes
- Survey competitor landscape: ✅ Mapped high/mid/low-end solutions

**Phase 2 (POC - 3-5 days)**:
- Working email monitoring system
- AI triage that extracts: service type, urgency, preferred date/time
- Mock booking confirmation flow
- Demo video (<2 min)

**Phase 3 (Validation - 1 week)**:
- Contact 20 businesses
- Get 5+ to watch demo
- Get 2+ to agree to pilot
- Document feedback and iterate

**Phase 4 (MVP - 2-3 weeks)**:
- Build based on validated feedback
- First paying customer

## Budget Tracking
- Research phase: $0 direct spend (used existing web search quota)
- POC phase estimate: $5-10 (API testing)
- Total allocated: $30-50 remaining this month

---

**Last Updated**: 2026-02-11
**Owner**: Koda
