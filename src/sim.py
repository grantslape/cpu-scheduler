"""Main Simulator"""
import logging
from pathlib import Path
from queue import PriorityQueue, Queue
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
        busy: If the CPU is being used or not TODO: Replace this with interpreting running_process?
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
                 log_level: int = logging.WARNING,
                 quantum: float = None):
        self.event_queue = PriorityQueue()
        self.process_queue = PriorityQueue() if method != Scheduler.Types['RR'] else Queue()
        self.done = []
        self.current_time = created_at
        self.busy = False
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

        timestamp = self.current_time.timestamp

        path = 'data'
        data_path = Path('{0}/{1}/{2}'.format(path, str(timestamp), Modeller.DATA_PATH))
        if not data_path.exists():
            data_path.mkdir(parents=True)
        plot_path = Path('{0}/{1}/{2}'.format(path, str(timestamp), Modeller.PLOT_PATH))
        if not plot_path.exists():
            plot_path.mkdir(parents=True)

        log_path = Path(str(data_path.parent) + '/logs')
        if not log_path.exists():
            log_path.mkdir()
        specific_path = '/scheduler_{0}_{1}'.format(method, process_rate)
        if method == Scheduler.Types['RR']:
            specific_path += '_{}'.format(quantum)
        specific_path += '.log'
        log_path = Path(str(log_path) + specific_path)
        log_path.touch()

        self.modeller = Modeller(path=path,
                                 created_at=timestamp)

        logging.basicConfig(filename=str(log_path),
                            level=log_level,
                            format='%(levelname)s - %(message)s')

    def process_event(self, event: Event):
        """Switch to process events"""
        if event.event_type == Event.Types['NEW']:
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
        self.scheduler.put_process(p)

    def _process_complete_event(self):
        """Process a completion event"""
        self.running_process.set_completed(self.current_time)
        self.done.append(self.running_process)
        logging.debug("%s: Finishing process: %s", self.current_time, self.running_process)
        self.running_process = None
        self.busy = False

    def _process_switch_event(self):
        """Process a round_robin style switch event"""
        logging.debug('%s: Processing switch event', self.current_time)
        self.scheduler.put_process(self.running_process)
        self.running_process = None
        self.busy = False

    def bootstrap(self):
        """Bootstrap Event Queue"""
        last_event_time = self.current_time
        for i in range(self.config['length']):
            activate_at = last_event_time.shift(
                seconds=rand_exp_float(self.config['rate']))

            process = Process(process_id=i + 1,
                              run_time=rand_exp_float(self.config['burst_lambda']),
                              created_at=activate_at)

            self.event_queue.put(
                Event(created_at=activate_at,
                      event_type=Event.Types['NEW'],
                      process=process))
            logging.debug('Queued creation event for process: %s', process)

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
                self.running_process.set_used(start=self.current_time,
                                              end=event.created_at)

            self.current_time = event.created_at
            self.process_event(event)

            self.scheduler.check_running_process()

        # TODO: Clean up and add quantum if needed
        tag = 'type' + str(self.scheduler.type) + '_burst' + \
              str(self.config['burst_lambda']) + '_rate' + \
              str(self.config['rate'])
        # path, filename = self.modeller.write_stats(self.done, tag)
        # self.modeller.plot(path, filename)

        logging.info('Sim done!')
