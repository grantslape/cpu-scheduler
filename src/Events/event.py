from arrow import Arrow, utcnow


class Event:
    """
    Basic Event class
    TODO: Document attributes
    """
    Types = {
        'NEW': 1,
        'COMPLETE': 2,
        'SWITCH': 3
    }

    def __init__(self,
                 created_at: Arrow = utcnow(),
                 event_type: int = None):
        self.created_at = created_at
        self.event_type = event_type

    def __lt__(self, other):
        """Implement comparable"""
        # Might need to use tuple of attributes
        return self.created_at < other.created_at
