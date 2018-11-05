"""Scheduler with baked in algorithm"""
import logging
from queue import PriorityQueue, Queue

from arrow import Arrow

from src.event import Event
from src.process import Process
from src.commons.commons import SCHEDULE_TYPES, EVENT_TYPES, rand_exp_float


class Scheduler:
    """
    Scheduler for Simulation.

    Algorithm to use for scheduling is baked into each scheduler to abstract
    away switch statements.

    TODO: Attributes:
        type: type of scheduling algorithm to use as enumerated in
            commons.SCHEDULE_TYPES
        quantum: Time quantum to preempt and switch to next process if applicable
        event_queue: PriorityQueue of events to be processed
        done: list of done processes
        process_queue: PriorityQueue|Queue of processes to be processed
        current_time: current system time, set by parent
        running_process: currently running process
    """
    def __init__(self, method: int, current_time: Arrow, config: dict):
        self.type = method
        self.config = config
        self.event_queue = PriorityQueue()
        self.done = []
        self.process_queue = PriorityQueue() if method != SCHEDULE_TYPES['RR'] else Queue()
        self.current_time = current_time
        self.running_process = None

    def check_running_process(self):
        """Check running process and adjust appropriately"""
        if self.type == SCHEDULE_TYPES['FCFS']:
            self._fcfs_queue_process()
        elif self.type == SCHEDULE_TYPES['SJF']:
            self._sjf_queue_process()
        elif self.type == SCHEDULE_TYPES['RR']:
            self._rr_queue_process()
        else:
            message = "Unknown schedule type: {}".format(self.type)
            logging.critical(message)
            raise Exception(message)

    def put_process(self, process: Process):
        """
        Insert a process into the queue
        :param process: Process to be inserted
        """
        logging.debug("%s: Inserting process: %s", self.current_time, process)
        if self.type == SCHEDULE_TYPES['FCFS']:
            self.process_queue.put((process.created_at, process))
        elif self.type == SCHEDULE_TYPES['SJF']:
            self.process_queue.put((process.run_time - process.used, process))
        elif self.type == SCHEDULE_TYPES['RR']:
            self.process_queue.put(process)

    def _start_process(self):
        """Start the next process from the queue"""
        # Hack to support simple queues.
        if isinstance(self.process_queue, PriorityQueue):
            self.running_process = self.process_queue.get()[1]
        else:
            self.running_process = self.process_queue.get()
        logging.debug("%s: starting process: %s",
                      self.current_time,
                      self.running_process)

    def _sjf_queue_process(self):
        """start a process with shortest job first scheduling"""
        if not self.process_queue.empty():
            # Do we need to preempt a process?
            if self.running_process:
                process = self.running_process
                remain = process.get_remaining()
                next_process = self.process_queue.queue[0][1]
                if next_process.run_time - next_process.used < remain:
                    logging.debug("%s: offloading process: %s", self.current_time, process)
                    self.put_process(process)
                    self._start_process()
            else:
                self._start_process()

        # Check if we need to queue a completion event
        if self.running_process:
            remain = self.running_process.get_remaining()
            estimate = self.current_time.shift(seconds=remain)
            if not self.event_queue.empty():
                next_time = self.event_queue.queue[0].created_at
                if not estimate < next_time:
                    return

            self.event_queue.put(
                Event(created_at=estimate,
                      event_type=EVENT_TYPES['COMPLETE'])
            )

    def _rr_queue_process(self):
        """start a process with round robin scheduling"""
        if not self.running_process and not self.process_queue.empty():
            self._start_process()
            if self.running_process.get_remaining() < self.config['quantum']:
                logging.debug('scheduling RR completion: %s', self.running_process)
                self.event_queue.put(
                    Event(
                        created_at=self.current_time.shift(seconds=self.running_process.get_remaining()),
                        event_type=EVENT_TYPES['COMPLETE']
                    )
                )
            else:
                self.event_queue.put(
                    Event(created_at=self.current_time.shift(seconds=self.config['quantum']),
                          event_type=EVENT_TYPES['SWITCH'])
                )

    def _fcfs_queue_process(self):
        """start a process with first come first served scheduling"""
        if not self.running_process and not self.process_queue.empty():
            self._start_process()
            # Queue completion event
            create = self.current_time.shift(seconds=self.running_process.run_time)
            self.event_queue.put(
                Event(created_at=create,
                      event_type=EVENT_TYPES['COMPLETE'])
            )

    def _sjf_insert_process(self, process: Process):
        """
        Insert process by sjf
        :param process: Process to be inserted
        """
        self.process_queue.put((process.run_time - process.used, process))

    def process_event(self, event: Event):
        """
        Switch to process events
        :param event: Event to be processed
        """
        if event.event_type == EVENT_TYPES['NEW']:
            self._process_new_event(event)
        elif event.event_type == EVENT_TYPES['COMPLETE']:
            self._process_complete_event()
        elif event.event_type == EVENT_TYPES['SWITCH']:
            self._process_switch_event()
        else:
            message = "Unknown event, terminating: {}".format(str(event))
            logging.critical(message)
            raise Exception(message)

    def _process_new_event(self, event: Event):
        """
        Process a new process event
        :param event: Event to be processed
        """
        p = event.process
        p.start_at = self.current_time
        self.put_process(p)

        # Spawn the next process
        activate_at = self.current_time.shift(
            seconds=rand_exp_float(self.config['rate']))
        event = self.create_event(activate_at, p.id + 1)
        self.event_queue.put(event)
        logging.debug('Queued creation event for process: %s', event.process)

    def create_event(self, activate_at: Arrow, p_id: int) -> Event:
        """Create a new process"""
        process = Process(
            process_id=p_id,
            run_time=rand_exp_float(self.config['burst_lambda']),
            created_at=activate_at
        )

        return Event(
            created_at=activate_at,
            event_type=EVENT_TYPES['NEW'],
            process=process
        )

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        logging.debug("%s: Finishing process: %s", self.current_time, self.running_process)
        self.running_process = None

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        logging.debug('%s: Processing switch event', self.current_time)
        self.put_process(self.running_process)
        self.running_process = None
