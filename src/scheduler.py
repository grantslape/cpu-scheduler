"""Scheduler with baked in algorithm"""
import logging

from src.event import Event


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

    def _fcfs_queue_process(self):
        """Queue a process with first come first served scheduling"""
        if not self.parent.busy and not self.parent.process_queue.empty():
            self.parent.running_process = self.parent.process_queue.get()
            logging.debug("starting process: %s", self.parent.running_process)
            self.parent.busy = True
            self.parent.running_process.start_at = self.parent.current_time
            # Queue completion event
            create = self.parent.current_time.shift(seconds=self.parent.running_process.run_time)
            self.parent.event_queue.put(
                Event(created_at=create,
                      event_type=Event.Types['COMPLETE']))

    # TODO: for both these, need to set process used
    def _sjf_queue_process(self):
        """Queue a process with shortest job first scheduling"""
        # TODO:
        # maybe check top event on insert - if completion time is beyond top,
        # don't schedule completion event
        # If a is a PriorityQueue object, You can use a.queue[0] to get the next item.
        # p queues are heap sorted
        pass

    def _rr_queue_process(self):
        """Queue a process with round robin scheduling"""
        # TODO: ONLY SCHEDULE COMPLETION IF WE WILL MAKE IT IN QUANTUM
        pass
