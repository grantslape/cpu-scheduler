import datetime


class Event:
    """Basic Event class"""
    Types = {
        'NEW': 1,
        'COMPLETE': 2,
        'SWITCH': 3
    }

    def __init__(self,
                 created_at: datetime=datetime.datetime.today(),
                 event_type: int=None):
        self.created_at = created_at
        self.event_type = event_type
