import datetime


class Event:
    """Basic Event class"""

    def __init__(self, created_at: datetime=datetime.today()):
        self.created_at = created_at
        self.event_type = None
