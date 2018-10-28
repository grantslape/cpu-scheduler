"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
import logging
import argparse
import numpy as np
import concurrent.futures
from arrow import utcnow, Arrow

from src.sim import Simulator
from src.scheduler import Scheduler


def main():
    """CLI Frontent"""
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', type=int, help='Number of trials')
    parser.add_argument('max_rate', type=int, help='max processes per second')
    parser.add_argument('seed', type=int, help='base seed for PRNG. base_seed + type + rate')
    parser.add_argument('-v', '--verbose', action='store_true', help='set log level to debug')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.WARNING
    prefix = utcnow()
    length = args.runs
    rates = [i + 1 for i in range(args.max_rate)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        for key, value in Scheduler.Types.items():
            kwargs = {
                'method': value,
                'prefix': prefix,
                'level': level,
                'quantum': 0.01,
                'rate': None,
                'length': length
            }

            for rate in rates:
                # concat base_seed
                np.random.seed(int(str(args.seed) + str(value) + str(rate)))
                kwargs['rate'] = rate
                executor.submit(run_sim, **kwargs)

            if key == 'RR':
                kwargs['quantum'] = 0.2
                for rate in rates:
                    np.random.seed(int(str(args.seed) + str(value) + str(rate)))
                    kwargs['rate'] = rate
                    executor.submit(run_sim, **kwargs)


def run_sim(method: int, prefix: Arrow, level: int, rate: int, length: int, quantum: float = None):
    """run sim with given parameters"""
    Simulator(
        method=method,
        log_level=level,
        created_at=prefix,
        quantum=quantum,
        process_rate=rate,
        length=length
    ).run()


if __name__ == '__main__':
    main()
