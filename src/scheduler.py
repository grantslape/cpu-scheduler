"""Scheduler with baked in algorithm"""
import logging

from src.event import Event
from src.process import Process


class Scheduler:
    """
    Scheduler for Simulation.

    Algorithm to use for scheduling is baked into each scheduler to abstract
    away switch statements.

    Attributes:
        parent: reference to the parent simulator
        method: type of scheduling algorithm to use as enumerated in
            Scheduler.Types

    """
    Types = {
        'FCFS': 1,
        'SJF': 2,
        'RR': 3
    }

    def __init__(self, parent, method: int):
        self.parent = parent
        self.type = method
        
    def check_running_process(self):
        """Check running process and adjust appropriately"""
        if self.type == self.Types['FCFS']:
            self._fcfs_queue_process()
        elif self.type == self.Types['SJF']:
            self._sjf_queue_process()
        elif self.type == self.Types['RR']:
            self._rr_queue_process()
        else:
            message = "Unknown schedule type: {}".format(self.type)
            logging.critical(message)
            raise Exception(message)

    def put_process(self, process: Process):
        """Insert a new process into the queue"""
        # TODO: need to insert (ranking, p) by different algo
        logging.debug("Inserting process: %s", process)
        if self.type == self.Types['FCFS']:
            self.parent.process_queue.put((process.created_at, process))
        elif self.type == self.Types['SJF']:
            self.parent.process_queue.put((process.run_time - process.used, process))
        elif self.type == self.Types['RR']:
            self.parent.process_queue.put((process.created_at, process))

    def _start_process(self):
        self.parent.running_process = self.parent.process_queue.get()[1]
        logging.debug("starting process: %s", self.parent.running_process)
        self.parent.busy = True
        self.parent.running_process.start_at = self.parent.current_time

    def _fcfs_queue_process(self):
        """start a process with first come first served scheduling"""
        if not self.parent.busy and not self.parent.process_queue.empty():
            self._start_process()
            # Queue completion event
            create = self.parent.current_time.shift(seconds=self.parent.running_process.run_time)
            self.parent.event_queue.put(
                Event(created_at=create,
                      event_type=Event.Types['COMPLETE'])
            )

    # TODO: for both these, need to set process used
    def _sjf_queue_process(self):
        """start a process with shortest job first scheduling"""
        if not self.parent.process_queue.empty():
            if self.parent.busy:
                process = self.parent.running_process
                remain = process.run_time - process.used
                next_process = self.parent.process_queue.queue[0][1]
                if next_process.run_time - next_process.used < remain:
                    logging.debug("offloading process: %s", process)
                    self.put_process(process)
                    self._start_process()
            else:
                self._start_process()
        #
        # # check for completion before next event
        # if self.parent.busy:
        #     next_time = self.parent.event_queue.queue[0].created_at
        #     process = self.parent.running_process
        #     remain = process.run_time - process.used
        #     estimate = self.parent.current_time.shift(seconds=remain)
        #     if estimate < next_time:
        #         self.parent.event_queue.put(
        #             Event(created_at=estimate,
        #                   event_type=Event.Types['COMPLETE']))

        if self.parent.busy:
            process = self.parent.running_process
            remain = process.run_time - process.used
            estimate = self.parent.current_time.shift(seconds=remain)
            if not self.parent.event_queue.empty():
                next_time = self.parent.event_queue.queue[0].created_at
                if not estimate < next_time:
                    return

            self.parent.event_queue.put(
                Event(created_at=estimate,
                      event_type=Event.Types['COMPLETE'])
            )

    def _rr_queue_process(self):
        """start a process with round robin scheduling"""
        # TODO: ONLY SCHEDULE COMPLETION IF WE WILL MAKE IT IN QUANTUM
        pass

    def _sjf_insert_process(self, process: Process):
        """Insert process by sjf"""
        self.parent.process_queue.put((process.run_time - process.used, process))
