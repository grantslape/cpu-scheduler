"""Main Simulator"""
import logging
from pathlib import Path
from queue import PriorityQueue, Queue
import numpy as np
from arrow import Arrow

from src.event import Event
from src.commons.commons import rand_exp_float, SCHEDULE_TYPES, EVENT_TYPES
from src.modeller import Modeller
from src.process import Process
from src.scheduler import Scheduler


class Simulator:
    """
    Simulator class

    For round-robin we may need to use a different queue
    For earliest job first we need to choose which job to process
    on each event process.

    Attributes:
        event_queue: Priority Queue of events to be processed
        process_queue: Priority Queue of processed to be executed
        done: list of completed processes
        current_time: the current system time
        usage: total CPU usage time in milliseconds
        length: number of trials to run
        burst_lambda: average process execution time
        running_process: currently running process
        created_at: used as file tag
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 created_at: Arrow,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1,
                 method: int = 1,
                 quantum: float = None):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue() if method != SCHEDULE_TYPES['RR'] else Queue()
        self.done = []
        self.current_time = created_at
        self.created_at = created_at
        self.usage = 0
        self.running_process = None

        self.config = {
            'length': length,
            'burst_lambda': burst_lambda,
            'rate': process_rate,
            'quantum': quantum
        }

        self.scheduler = Scheduler(parent=self,
                                   method=method,
                                   quantum=self.config['quantum'])

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
        self.scheduler.put_process(p)

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        logging.debug("%s: Finishing process: %s", self.current_time, self.running_process)
        self.running_process = None

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        logging.debug('%s: Processing switch event', self.current_time)
        self.scheduler.put_process(self.running_process)
        self.running_process = None

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.config['length']):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.config['rate']))

            process = Process(
                process_id=i + 1,
                run_time=rand_exp_float(self.config['burst_lambda']),
                created_at=activate_at
            )

            self.event_queue.put(
                Event(
                    created_at=activate_at,
                    event_type=EVENT_TYPES['NEW'],
                    process=process
                )
            )
            logging.debug('Queued creation event for process: %s', process)
            last_event_time = activate_at

    def run(self):
        """Run the whole simulation"""
        logging.info('%s: Bootstrapping event queue', self.current_time)
        self.bootstrap()

        logging.info('%s: Beginning main event loop', self.current_time)
        while not self.event_queue.empty():
            event = self.event_queue.get()
            if self.running_process:
                # Update usage time if CPU was busy in prev interval
                diff = event.created_at - self.current_time
                self.usage += diff.total_seconds()
                self.running_process.set_used(
                    start=self.current_time,
                    end=event.created_at
                )
            self.current_time = event.created_at
            self.process_event(event)
            self.scheduler.check_running_process()

        members = (
            self.scheduler.type,
            self.config['burst_lambda'],
            self.config['rate'],
            self.config['quantum']
        )
        tag = 'type{0}_burst{1}_rate{2}_quantum{3}'.format(*members)

        logging.info('%s: Sim %s offloading!', self.current_time, tag)

        return self.offload(tag)

    def offload(self, tag: str) -> Path:
        """
        Offload Sim resources and write stats
        :param tag: unique tag to apply to csv
        :return: path to created file
        """
        modeller = Modeller(path='data')
        logging.info('%s: Writing run stats', self.current_time)
        kwargs = {
            'in_list': np.array(self.done),
            'path': tag,
            'created_at': self.created_at.timestamp,
            'length': self.config['length'],
            'usage': self.usage,
            'total_time': (self.current_time - self.created_at).total_seconds(),
            'given_lambda': self.config['rate']
        }
        modeller.write_stats(**kwargs)

        return Path()
