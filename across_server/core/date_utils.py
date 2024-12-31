from datetime import datetime, timezone


def convert_to_utc(date: str | datetime) -> datetime:
    """
    Converts datetimes or strings to UTC and remove timezone info 
    Timezone-naive datetimes are needed for sqlalchemy
    This assumes that any passed timezone-naive datetime/string
    is already in UTC (as opposed to local time, for example)
    """
    if isinstance(date, str):
        date_from_str = datetime.fromisoformat(date)
        if date_from_str.tzinfo:
            return date_from_str.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            return date_from_str
        
    elif isinstance(date, datetime):
        if date.tzinfo:
            return date.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            return date
    else:
        raise ValueError("Date must be a string or datetime")