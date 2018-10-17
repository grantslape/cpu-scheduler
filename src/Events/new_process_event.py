"""New Process Event"""
from arrow import Arrow

from src.Events.event import Event
from src.processes.process import Process


class NewProcessEvent(Event):
    """
    New Process event
    TODO: Document attributes
    """
    def __init__(self, created_at: Arrow, process: Process):
        super().__init__(created_at)
        self.process = process
