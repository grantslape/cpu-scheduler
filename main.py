"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
import logging

from src.sim import Simulator
from src.scheduler import Scheduler


def main():
    sim = Simulator(method=Scheduler.Types['FCFS'],
                    log_level=logging.DEBUG)
    sim.run()


if __name__ == '__main__':
    main()
