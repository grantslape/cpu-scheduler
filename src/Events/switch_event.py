"""Time-slice Switch event"""
from arrow import Arrow

from src.Events.event import Event


class SwitchEvent(Event):

    def __init__(self, created_at: Arrow):
        super().__init__(created_at)
