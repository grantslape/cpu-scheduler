"""Main Simulator"""
from queue import PriorityQueue

from arrow import utcnow


class Simulator:
    def __init__(self):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue()
        self.done = []
        self.current_time = utcnow()
        self.busy = False
        self.usage = 0

    def process_event(self):
        """Switch to process events"""
        pass

    def write_stats(self):
        """Write run statistics"""

    def run(self):
        """Run the whole simulation"""
        print('Run the simulator and things')
        pass
