from datetime import date, datetime


def month_date_range(year: int, month: int) -> tuple[date, date]:
    """(first day of month, first day of next month) — end date is exclusive."""
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def parse_date_from_str(raw_date) -> date:
    if isinstance(raw_date, date):
        return raw_date
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw_date, fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError(f"Unsupported date format: {raw_date}")