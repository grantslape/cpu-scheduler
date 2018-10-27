"""Main Simulator"""
from queue import PriorityQueue
from arrow import utcnow
import logging

from src.Events.event import Event
from src.commons.commons import rand_exp_float
from src.processes.process import Process
from src.scheduler import Scheduler


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
    def __init__(self,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1,
                 method: int = 1,
                 log_level: int = logging.WARNING):
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

        self.scheduler = Scheduler(parent=self, method=method)

        logging.basicConfig(filename='logs/scheduler.log',
                            level=log_level,
                            format='%(levelname)s - %(message)s')

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
            message = "Unknown event, terminating: {}".format(str(event))
            logging.critical(message)
            raise Exception(message)

    def _process_new_event(self, event: Event):
        """Process a new process event"""
        p = event.process
        p.start_at = self.current_time
        # TODO: need to insert (ranking, p) by different
        # TODO: scheduling algorithm
        logging.debug("Inserting process: {}".format(p))
        self.process_queue.put(p)

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        logging.debug("Finishing process: {}".format(str(self.running_process)))
        self.running_process = None
        self.busy = False

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        # TODO: IMPLEMENT
        pass

    def _fcfs_queue_process(self):
        """Queue a process with FCFS scheduling"""
        if not self.busy and not self.process_queue.empty():
            self.running_process = self.process_queue.get()
            logging.debug("starting process: {}".format(str(self.running_process)))
            self.busy = True
            self.running_process.start_at = self.current_time
            # Queue completion event
            self.event_queue.put(
                Event(created_at=self.current_time.shift(seconds=self.running_process.run_time),
                      event_type=Event.Types['COMPLETE']))

    def check_running_process(self):
        """Check running process and adjust appropriately"""
        if self.scheduler.type == self.scheduler.Types['FCFS']:
            self._fcfs_queue_process()
        # TODO: for both these, need to set process used
        elif self.scheduler.type == self.scheduler.Types['SJF']:
            # TODO: NEED TO UNSCHEDULE COMPLETION EVENT
            # maybe check top event on insert - if completion time is beyond top,
            # don't schedule completion event
            # If a is a PriorityQueue object, You can use a.queue[0] to get the next item.
            # p queues are heap sorted
            pass
        elif self.scheduler.type == self.scheduler.Types['RR']:
            # TODO: ONLY SCHEDULE COMPLETION IF WE WILL MAKE IT IN QUANTUM
            pass
        else:
            message = "Unknown schedule type: {}".format(self.scheduler.type)
            logging.critical(message)
            raise Exception(message)

    def write_stats(self):
        """Write run statistics"""
        # TODO: CSV WRITER
        # MAYBE DATA MODELLER IN ANOTHER CLASS
        pass

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.length):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.rate))

            p = Process(process_id=i + 1,
                        run_time=rand_exp_float(self.burst_lambda),
                        created_at=activate_at)

            self.event_queue.put(
                Event(created_at=activate_at,
                      event_type=Event.Types['NEW'],
                      process=p))
            logging.debug('Queued creation event for process: {}'.format(str(p)))

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

            self.check_running_process()

        logging.info('Sim done!')
