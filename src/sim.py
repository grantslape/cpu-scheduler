"""Main Simulator"""
from queue import PriorityQueue


class Simulator:
    def __init__(self):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue()

    def process_event(self):
        """Switch to process events"""
        pass

    def write_stats(self):
        """Write run statistics"""

    def run(self):
        """Run the whole simulation"""
        print('Run the simulator and things')
        pass
