"""Main Simulator"""
from queue import PriorityQueue
from arrow import utcnow

from src.Events.event import Event
from src.commons.commons import rand_exp_float
from src.processes.process import Process


class Simulator:
    """
    Simulator class

    For round-robin we may need to use a different queue
    FOr earliest job first we need to choose which job to process
    on each event process.

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
    Method = {
        'FCFS': 1,
        'SJF': 2,
        'RR': 3
    }

    def __init__(self,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1,
                 method: int = 1):
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
        self.schedule = method

    def process_event(self, event: Event):
        """Switch to process events"""
        if event.event_type == Event.Types['NEW']:
            # TODO: in SJF, maybe switch process
            self._process_new_event(event)
        elif event.event_type == Event.Types['COMPLETE']:
            self._process_complete_event()
        elif event.event_type == Event.Types['SWITCH']:
            self._process_switch_event()
        else:
            raise Exception("Unknown event, terminating: {}".format(str(event)))

    def _process_new_event(self, event: Event):
        """Process a new process event"""
        p = event.process
        p.start_at = self.current_time
        # TODO: need to insert (ranking, p) by different
        # TODO: scheduling algorithm
        self.process_queue.put(p)

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        self.running_process = None
        self.busy = False

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        # TODO: IMPLEMENT
        pass

    def write_stats(self):
        """Write run statistics"""

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.length):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.rate))

            p = Process(process_id=i,
                        run_time=rand_exp_float(self.burst_lambda),
                        created_at=activate_at)

            self.event_queue.put(
                Event(created_at=activate_at,
                      event_type=Event.Types['NEW'],
                      process=p))

            last_event_time = activate_at

    def run(self):
        """Run the whole simulation"""
        self.bootstrap()

        while not self.event_queue.empty():
            event = self.event_queue.get()
            if self.busy:
                # Update usage time if CPU was busy in prev interval
                diff = event.created_at - self.current_time
                self.usage += diff.total_seconds()

            self.current_time = event.created_at
            self.process_event(event)

            # TODO: THIS DOES NOT WORK FOR SHORTEST JOB FIRST
            # TODO: so factor this out to algo type function to run here
            if not self.busy and not self.process_queue.empty():
                self.running_process = self.process_queue.get()
                self.busy = True
                # TODO: schedule complete event.

        print("Sim done!")
