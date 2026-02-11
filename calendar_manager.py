#!/usr/bin/env python3
"""
Calendar integration for checking availability and booking appointments.

MVP version: Mock implementation that simulates Google Calendar behavior.
Production version would use actual Google Calendar API with OAuth.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class CalendarManager:
    """
    Manages calendar availability and bookings.
    
    MVP: Mock implementation with hardcoded business hours.
    Production: Will use Google Calendar API.
    """
    
    def __init__(self, calendar_id: Optional[str] = None):
        """
        Initialize calendar manager.
        
        Args:
            calendar_id: Google Calendar ID (for production)
        """
        self.calendar_id = calendar_id
        
        # Mock business hours (9 AM - 5 PM, Mon-Fri)
        self.business_hours = {
            "start_hour": 9,
            "end_hour": 17,
            "working_days": [0, 1, 2, 3, 4]  # Monday-Friday
        }
        
        # Mock existing bookings (in production, fetched from Google Calendar)
        self.mock_bookings = []
    
    def get_availability(self, date_range_days: int = 7, service_duration_minutes: int = 60) -> List[Dict]:
        """
        Get available time slots for the next N days.
        
        Args:
            date_range_days: Number of days to check
            service_duration_minutes: Duration of service appointment
            
        Returns:
            List of available slots: [{"start": datetime, "end": datetime}, ...]
        """
        available_slots = []
        
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day_offset in range(date_range_days):
            check_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() not in self.business_hours["working_days"]:
                continue
            
            # Generate slots for this day
            current_hour = self.business_hours["start_hour"]
            while current_hour < self.business_hours["end_hour"]:
                slot_start = check_date.replace(hour=current_hour, minute=0)
                slot_end = slot_start + timedelta(minutes=service_duration_minutes)
                
                # Check if slot is in the future
                if slot_start > datetime.now():
                    # In production: check against actual Google Calendar bookings
                    if not self._is_slot_booked(slot_start, slot_end):
                        available_slots.append({
                            "start": slot_start,
                            "end": slot_end,
                            "duration_minutes": service_duration_minutes
                        })
                
                # Move to next slot (assuming 1-hour slots)
                current_hour += 1
        
        return available_slots
    
    def _is_slot_booked(self, start: datetime, end: datetime) -> bool:
        """
        Check if a time slot is already booked.
        
        In production: query Google Calendar API.
        MVP: check mock bookings list.
        """
        for booking in self.mock_bookings:
            booking_start = booking["start"]
            booking_end = booking["end"]
            
            # Check for overlap
            if (start < booking_end) and (end > booking_start):
                return True
        
        return False
    
    def book_appointment(
        self,
        start_time: datetime,
        duration_minutes: int,
        customer_name: str,
        customer_email: str,
        service_type: str
    ) -> Dict:
        """
        Book an appointment.
        
        Args:
            start_time: When the appointment starts
            duration_minutes: How long the appointment is
            customer_name: Customer's name
            customer_email: Customer's email
            service_type: Type of service being booked
            
        Returns:
            Booking confirmation dict
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check if slot is available
        if self._is_slot_booked(start_time, end_time):
            return {
                "success": False,
                "error": "Time slot is no longer available",
                "booking_id": None
            }
        
        # Create booking
        booking = {
            "booking_id": f"mock_{int(start_time.timestamp())}",
            "start": start_time,
            "end": end_time,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "service_type": service_type,
            "status": "confirmed",
            "created_at": datetime.now()
        }
        
        # In production: create Google Calendar event
        self.mock_bookings.append(booking)
        
        return {
            "success": True,
            "booking_id": booking["booking_id"],
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "confirmation_sent": True
        }
    
    def get_next_available_slots(self, count: int = 5, urgency: str = "flexible") -> List[Dict]:
        """
        Get the next N available slots, adjusted for urgency.
        
        Args:
            count: Number of slots to return
            urgency: "emergency", "today", "this_week", or "flexible"
            
        Returns:
            List of next available slots
        """
        if urgency == "emergency":
            # Check next 24 hours
            slots = self.get_availability(date_range_days=1)
        elif urgency == "today":
            # Check today only
            slots = self.get_availability(date_range_days=1)
        elif urgency == "this_week":
            # Check next 7 days
            slots = self.get_availability(date_range_days=7)
        else:  # flexible
            # Check next 2 weeks
            slots = self.get_availability(date_range_days=14)
        
        return slots[:count]
    
    def format_slot_for_customer(self, slot: Dict) -> str:
        """
        Format a time slot in a customer-friendly way.
        
        Args:
            slot: Slot dict with start/end datetime
            
        Returns:
            Formatted string like "Wednesday, Feb 12 at 10:00 AM"
        """
        start = slot["start"]
        return start.strftime("%A, %b %d at %I:%M %p")


def test_calendar():
    """Test calendar functionality"""
    
    print("Testing Calendar Manager")
    print("=" * 60)
    print()
    
    calendar = CalendarManager()
    
    # Test 1: Get availability
    print("Test 1: Get next 10 available slots")
    slots = calendar.get_availability(date_range_days=7)
    
    print(f"Found {len(slots)} available slots in next 7 days")
    print("\nFirst 5 slots:")
    for i, slot in enumerate(slots[:5], 1):
        formatted = calendar.format_slot_for_customer(slot)
        print(f"  {i}. {formatted}")
    print()
    
    # Test 2: Get slots by urgency
    print("Test 2: Get slots for 'today' urgency")
    urgent_slots = calendar.get_next_available_slots(count=3, urgency="today")
    print(f"Found {len(urgent_slots)} slots today:")
    for slot in urgent_slots:
        print(f"  - {calendar.format_slot_for_customer(slot)}")
    print()
    
    # Test 3: Book an appointment
    if slots:
        print("Test 3: Book an appointment")
        first_slot = slots[0]
        result = calendar.book_appointment(
            start_time=first_slot["start"],
            duration_minutes=60,
            customer_name="John Smith",
            customer_email="john@example.com",
            service_type="hvac_repair"
        )
        
        print(f"Booking result: {json.dumps(result, indent=2, default=str)}")
        print()
    
    # Test 4: Check that booked slot is no longer available
    print("Test 4: Verify slot is no longer available")
    new_slots = calendar.get_availability(date_range_days=7)
    print(f"Slots before booking: {len(slots)}")
    print(f"Slots after booking: {len(new_slots)}")
    print(f"Difference: {len(slots) - len(new_slots)} (should be 1)")
    print()
    
    print("✅ All tests complete")


if __name__ == "__main__":
    test_calendar()
