"""Main Simulator"""
import logging
import os
from queue import PriorityQueue
from arrow import Arrow

from src.event import Event
from src.commons.commons import rand_exp_float
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
        busy: If the CPU is being used or not
        usage: total CPU usage time in milliseconds
        length: number of trials to run
        burst_lambda:
        running_process:
        created_at: used as file tag
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 created_at: Arrow,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1,
                 method: int = 1,
                 log_level: int = logging.WARNING):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue()
        self.done = []
        self.current_time = created_at
        self.busy = False
        self.usage = 0
        self.running_process = None

        self.config = {
            'length': length,
            'burst_lambda': burst_lambda,
            'rate': process_rate
        }

        self.scheduler = Scheduler(parent=self, method=method)

        path = 'data'
        timestamp = self.current_time.timestamp
        os.mkdir(path + '/' + str(timestamp))
        os.mkdir(path + '/' + str(timestamp) + '/' + Modeller.DATA_PATH)
        os.mkdir(path + '/' + str(timestamp) + '/' + Modeller.PLOT_PATH)
        self.modeller = Modeller(path=path,
                                 created_at=timestamp)

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
        logging.debug("Inserting process: %s", p)
        self.process_queue.put(p)

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        logging.debug("Finishing process: %s", self.running_process)
        self.running_process = None
        self.busy = False

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        # TODO: IMPLEMENT
        pass

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.config['length']):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.config['rate']))

            p = Process(process_id=i + 1,
                        run_time=rand_exp_float(self.config['burst_lambda']),
                        created_at=activate_at)

            self.event_queue.put(
                Event(created_at=activate_at,
                      event_type=Event.Types['NEW'],
                      process=p))
            logging.debug('Queued creation event for process: %s', p)

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

            self.scheduler.check_running_process()

        tag = 'type' + str(self.scheduler.type) + '_burst' + \
              str(self.config['burst_lambda']) + '_rate' + \
              str(self.config['rate'])
        path, filename = self.modeller.write_stats(self.done, tag)
        self.modeller.plot(path, filename)
        logging.info('Sim done!')
