from datetime import date, datetime, timedelta
from calendar import monthrange
from workers import Response, handler

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


def build_paydays(dates):
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
    paydays = find_paydays()
    body = build_paydays(paydays)
    return Response(body)
