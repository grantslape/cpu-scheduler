"""Main Simulator"""
import logging
from pathlib import Path
import numpy as np
from arrow import Arrow

from src.commons.commons import rand_exp_float
from src.modeller import Modeller
from src.scheduler import Scheduler


class Simulator:
    """
    Simulator class

    For round-robin we may need to use a different queue
    For earliest job first we need to choose which job to process
    on each event process.

    Attributes:
        current_time: the current system time
        usage: total CPU usage time in milliseconds
        burst_lambda: average process execution time
        process_rate: rate of process arrival
        length: length of simulation in processes
        quantum: time quantum (only for round robin)
        created_at: used as file tag
        method: scheduling method (see commons.SCHEDULE_TYPES)
    """
    def __init__(self,
                 created_at: Arrow,
                 length: int = 100,
                 burst_lambda: float = 0.06,
                 process_rate: int = 1,
                 method: int = 1,
                 quantum: float = None):
        self.current_time = created_at
        self.created_at = created_at
        self.usage = 0

        self.config = {
            'length': length,
            'burst_lambda': burst_lambda,
            'rate': process_rate,
            'quantum': quantum
        }

        self.scheduler = Scheduler(method=method,
                                   current_time=self.current_time,
                                   config=self.config)

    def update_current_time(self, new_time: Arrow):
        """
        Update system time
        :param new_time: Arrow datetime
        """
        self.current_time = new_time
        self.scheduler.current_time = new_time

    def bootstrap(self):
        """
        Queue 1 creation event to start simulation
        """
        activate_at = self.current_time.shift(
            seconds=rand_exp_float(self.config['rate'])
        )
        self.scheduler.event_queue.put(self.scheduler.create_event(activate_at, 1))

    def run(self) -> Path:
        """Run the whole simulation"""
        logging.info('%s: Bootstrapping event queue', self.current_time)
        self.bootstrap()

        logging.info('%s: Beginning main event loop', self.current_time)
        while len(self.scheduler.done) < self.config['length']:
            event = self.scheduler.event_queue.get()
            if self.scheduler.running_process:
                # Update usage time if CPU was busy in prev interval
                diff = event.created_at - self.current_time
                self.usage += diff.total_seconds()
                self.scheduler.running_process.set_used(
                    start=self.current_time,
                    end=event.created_at
                )
            self.update_current_time(event.created_at)
            self.scheduler.process_event(event)
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
            'in_list': np.array(self.scheduler.done),
            'path': tag,
            'created_at': self.created_at.timestamp,
            'length': self.config['length'],
            'usage': self.usage,
            'total_time': (self.current_time - self.created_at).total_seconds(),
            'given_lambda': self.config['rate'],
            'type': self.scheduler.type,
            'quantum': self.config['quantum']
        }

        return modeller.write_stats(**kwargs)
