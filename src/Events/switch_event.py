import datetime

from src.Events.event import Event


class SwitchEvent(Event):
    """Time-slice Switch event"""

    def __init__(self, created_at: datetime = datetime.datetime.today()):
        super().__init__(created_at, Event.Types['SWITCH'])
