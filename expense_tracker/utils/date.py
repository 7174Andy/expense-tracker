from datetime import date, datetime

def parse_date_from_str(raw_date) -> date:
    if isinstance(raw_date, date):
        return raw_date
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw_date, fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError(f"Unsupported date format: {raw_date}")