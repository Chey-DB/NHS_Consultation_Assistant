from datetime import datetime, timedelta

def is_within_five_minutes(last_call_time: datetime) -> bool:
    """Check if the given timestamp is within the last 5 minutes."""
    return datetime.now() - last_call_time <= timedelta(minutes=5)

def calculate_call_duration(start_time: datetime, end_time: datetime) -> timedelta:
    """Calculate the duration of a call."""
    return end_time - start_time
