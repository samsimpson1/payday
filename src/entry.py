from datetime import date, datetime, timedelta
from calendar import monthrange
from dataclasses import dataclass
from typing import List, Optional
from workers import Response, handler

@dataclass
class CalendarEvent:
    """Represents a calendar event that can be added to an iCal calendar."""
    summary: str
    start_date: date
    uid: str
    end_date: Optional[date] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.end_date is None:
            self.end_date = self.start_date

def find_payday_for(given_date):
    # paid on second to last day of month
    day = monthrange(given_date.year, given_date.month)[1]
    work_days_sub = 0

    while True:
        prop_date = date(given_date.year, given_date.month, day)
        weekday = prop_date.weekday()
        if work_days_sub == 1 and weekday < 5:
            return prop_date
        day -= 1
        if weekday < 5:
            work_days_sub += 1
        if day < 0:
            raise Exception(f"Failed to find pay day for {given_date}")

def find_paydays():
    """Find payday dates for the next 12 months."""
    current = datetime.now()
    year = current.year
    month = current.month
    paydays = [find_payday_for(date(year, month, 1))]

    for i in range(0, 11):
        if month + 1 > 12:
            year += 1
            month = 1
        else:
            month += 1
        paydays.append(find_payday_for(date(year, month, 1)))

    return paydays

def generate_payday_events() -> List[CalendarEvent]:
    """Generate payday events for the next 12 months."""
    paydays = find_paydays()
    events = []
    
    for payday_date in paydays:
        month_name = payday_date.strftime("%B")
        event = CalendarEvent(
            summary=f"{month_name} Pay Day",
            start_date=payday_date,
            uid=f"{payday_date.year}{payday_date.month}@payday.simpson.id"
        )
        events.append(event)
    
    return events


def build_calendar(events: List[CalendarEvent]) -> str:
    """Build an iCal calendar from a list of events."""
    current = datetime.now().strftime("%Y%m%dT%H%M%S")

    header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//payday.simpson.id//DSIT Payday Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH"""

    for event in events:
        formatted_start = event.start_date.strftime("%Y%m%d")
        formatted_end = event.end_date.strftime("%Y%m%d")
        
        event_str = f"""
BEGIN:VEVENT
SUMMARY:{event.summary}
UID:{event.uid}
SEQUENCE:0
STATUS:CONFIRMED
DTSTART:{formatted_start}
DTEND:{formatted_end}
DTSTAMP:{current}
END:VEVENT"""
        header += event_str

    header += "\nEND:VCALENDAR"

    return header

def build_paydays(dates):
    """Legacy function - maintained for backwards compatibility."""
    current = datetime.now().strftime("%Y%m%dT%H%M%S")

    header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//payday.simpson.id//DSIT Payday Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH"""

    for date in dates:
        formatted_date = date.strftime("%Y%m%d")
        month_name = date.strftime("%B")
        date_str = f"""
BEGIN:VEVENT
SUMMARY:{month_name} Pay Day
UID:{date.year}{date.month}@payday.simpson.id
SEQUENCE:0
STATUS:CONFIRMED
DTSTART:{formatted_date}
DTEND:{formatted_date}
DTSTAMP:{current}
END:VEVENT"""
        header += date_str

    header += "\nEND:VCALENDAR"

    return header

@handler
async def on_fetch(request, env):
    # Generate all events for the calendar
    events = []
    
    # Add payday events
    events.extend(generate_payday_events())
    
    # FUTURE: To add more event types, create new generate_*_events() functions
    # and add them here. Examples:
    #
    # events.extend(generate_holiday_events())
    # events.extend(generate_meeting_events()) 
    # events.extend(generate_deadline_events())
    #
    # Each generate_*_events() function should return a List[CalendarEvent]
    
    # Build and return the calendar
    body = build_calendar(events)
    return Response(body)
