"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
import logging
import argparse
import concurrent.futures
import numpy as np
from arrow import utcnow, Arrow

from src.sim import Simulator
from src.scheduler import Scheduler


def main():
    """CLI Frontent"""
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', type=int, help='Number of trials')
    parser.add_argument('max_rate', type=int, help='max processes per second')
    parser.add_argument('seed', type=int, help='base seed for PRNG. base_seed + type + rate')
    parser.add_argument('-v', '--verbose', action='store_true', help='logs use a lot of disk space')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    prefix = utcnow()
    length = args.runs
    rates = [i + 1 for i in range(args.max_rate)]
    results = []

    Simulator.create_logger(log_level=level, tag=str(prefix.timestamp))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(rates) * 4) as executor:
        for key, value in Scheduler.Types.items():
            kwargs = {
                'method': value,
                'prefix': prefix,
                'quantum': 0.01,
                'rate': None,
                'length': length
            }

            for rate in rates:
                # concat base_seed
                np.random.seed(int(str(args.seed) + str(value) + str(rate)))
                kwargs['rate'] = rate
                results.append(executor.submit(run_sim, **kwargs))

            if key == 'RR':
                kwargs['quantum'] = 0.2
                for rate in rates:
                    np.random.seed(int(str(args.seed) + str(value) + str(rate)))
                    kwargs['rate'] = rate
                    results.append(executor.submit(run_sim, **kwargs))

    for result in results:
        logging.debug(result.result())
    generate_plots()


def generate_plots():
    """
    TODO: Implement.  Glob for high pattern in data directory
    :return:
    """
    pass


def run_sim(method: int, prefix: Arrow, rate: int, length: int, quantum: float = None):
    """
    run sim with given parameters
    :param method:
    :param prefix:
    :param level:
    :param rate:
    :param length:
    :param quantum:
    :return:
    """
    Simulator(
        method=method,
        created_at=prefix,
        quantum=quantum,
        process_rate=rate,
        length=length
    ).run()


if __name__ == '__main__':
    main()
