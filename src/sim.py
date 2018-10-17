"""Main Simulator"""
from queue import PriorityQueue
from arrow import utcnow

from src.Events.event import Event
from src.commons.commons import rand_exp_float
from src.processes.process import Process


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
        length: number of trials to run
        burst_lambda:
        running_process:
    """
    def __init__(self,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue()
        self.done = []
        self.current_time = utcnow()
        self.busy = False
        self.usage = 0
        self.length = length
        self.burst_lambda = burst_lambda
        self.rate = process_rate
        self.running_process = None

    def process_event(self, event: Event):
        """Switch to process events"""
        if event.event_type == Event.Types['NEW']:
            self.process_new_event(event)
        elif event.event_type == Event.Types['COMPLETE']:
            # TODO: COMPLETE
            pass
        elif event.event_type == Event.Types['SWITCH']:
            # TODO: COMPLETE
            pass
        else:
            raise Exception("Unknown event, terminating: {}".format(str(event)))

    def process_new_event(self, event: Event):
        """Process a new process event"""


    def write_stats(self):
        """Write run statistics"""

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.length):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.rate)
            )
            p = Process(process_id=i,
                        run_time=rand_exp_float(self.burst_lambda))
            self.event_queue.put(
                Event(created_at=activate_at,
                      event_type=Event.Types['NEW'],
                      process=p))
            last_event_time = activate_at

    def run(self):
        """Run the whole simulation"""
        print('Run the simulator and things')
        self.bootstrap()
        while not self.event_queue.empty():
            # TODO: Update clock and usage first
            event = self.event_queue.get()
            if self.busy:
                # Update usage time if CPU was busy in prev interval
                diff = event.created_at - self.current_time
                self.usage += diff.total_seconds()

            self.current_time = event.created_at
            self.process_event(event)

            if not self.busy and not self.process_queue.empty():
                self.running_process = self.process_queue.get()
