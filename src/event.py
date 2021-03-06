"""Event class"""
from arrow import Arrow, utcnow

from src.process import Process


class Event:
    """
    Basic Event class
    """
    def __init__(self,
                 created_at: Arrow = utcnow(),
                 event_type: int = None,
                 process: Process = None):
        """
        Event Constructor
        :param created_at:
        :param event_type:
        :param process:
        """
        self.created_at = created_at
        self.event_type = event_type
        self.process = process

    def __lt__(self, other):
        """Implement comparable"""
        return self.created_at < other.created_at
