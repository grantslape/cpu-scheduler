"""CompleteProcessEvent"""
from arrow import Arrow

from src.Events.event import Event


class CompleteProcessEvent(Event):
    """
    Complete current process event.  can check IDs for integrity
    TODO: Document attributes
    """
    def __init__(self, created_at: Arrow, process_id: int):
        super().__init__(created_at)
        self.process_id = process_id
