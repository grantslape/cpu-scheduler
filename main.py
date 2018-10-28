"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
import logging
from arrow import utcnow

from src.sim import Simulator
from src.scheduler import Scheduler


def main():
    prefix = utcnow()

    sim = Simulator(
        method=Scheduler.Types['RR'],
        log_level=logging.DEBUG,
        created_at=prefix,
        quantum=0.1
    )
    sim.run()


if __name__ == '__main__':
    main()
