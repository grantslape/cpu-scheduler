"""Main Simulator"""
from queue import PriorityQueue

from arrow import utcnow


class Simulator:
    """
    Simulator class
    Attributes:
        event_queue: Priority Queue of events to be processed
        process_queue: Priority Queue of processed to be executed
        done: list of completed processes
        current_time: the current system time
        busy: If the CPU is being used or not
        usage: total CPU usage time in milliseconds
    """
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
