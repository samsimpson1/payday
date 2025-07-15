# Adding New Event Types to the Calendar

The calendar system has been refactored to easily support adding new event types. Here's how to add them:

## 1. Create an Event Generator Function

Create a new function that returns a list of `CalendarEvent` objects:

```python
def generate_holiday_events() -> List[CalendarEvent]:
    """Generate holiday events for the calendar."""
    current_year = datetime.now().year
    holidays = [
        (date(current_year, 1, 1), "New Year's Day"),
        (date(current_year, 7, 4), "Independence Day"),
        (date(current_year, 12, 25), "Christmas Day"),
    ]
    
    events = []
    for holiday_date, holiday_name in holidays:
        event = CalendarEvent(
            summary=f"🎉 {holiday_name}",
            start_date=holiday_date,
            uid=f"holiday-{holiday_date.strftime('%Y%m%d')}@payday.simpson.id",
            description=f"Public holiday: {holiday_name}"
        )
        events.append(event)
    
    return events
```

## 2. Add to Main Handler

In the `on_fetch` function, add your new event generator:

```python
@handler
async def on_fetch(request, env):
    # Generate all events for the calendar
    events = []
    
    # Add payday events
    events.extend(generate_payday_events())
    
    # Add your new event type
    events.extend(generate_holiday_events())
    
    # Build and return the calendar
    body = build_calendar(events)
    return Response(body)
```

## CalendarEvent Structure

The `CalendarEvent` dataclass supports:

- `summary`: Event title (required)
- `start_date`: Event start date (required)  
- `uid`: Unique identifier (required)
- `end_date`: Event end date (optional, defaults to start_date)
- `description`: Event description (optional)

## Example Event Types You Could Add

- **Meeting Events**: Recurring team meetings, deadlines
- **Holiday Events**: Company holidays, public holidays
- **Reminder Events**: Tax deadlines, performance reviews
- **Project Events**: Milestone dates, release dates
- **Personal Events**: Birthdays, anniversaries

Each event type should have its own `generate_*_events()` function for clean separation of concerns.