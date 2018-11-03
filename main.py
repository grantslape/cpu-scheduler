"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
import logging
import argparse
import concurrent.futures
from pathlib import Path

import numpy as np
from arrow import utcnow, Arrow

from src.modeller import Modeller
from src.sim import Simulator
from src.commons.commons import SCHEDULE_TYPES


def create_logger(log_level: int, tag: str):
    """
    !! CALL ONCE PER GROUP OF SIMULATIONS !!
    Static method to create logger and data directories
    :param log_level: level to set global logger
    :param tag: Sim grouping tag (unix timestamps)
    """
    # Create data directories for this run (and any others in the set)
    data_path = Modeller.get_data_path(tag)
    if not data_path.exists():
        data_path.mkdir(parents=True)
    plot_path = Modeller.get_plot_path(tag)
    if not plot_path.exists():
        plot_path.mkdir(parents=True)

    log_path = Path('{0}{1}'.format(str(data_path.parent), '/logs'))
    if not log_path.exists():
        log_path.mkdir()
    specific_path = '/scheduler.log'
    log_path = Path('{0}{1}'.format(str(log_path), specific_path))
    if not log_path.exists():
        log_path.touch()

    logging.basicConfig(
        filename=str(log_path),
        level=log_level,
        format='%(threadName)s: %(levelname)s - %(message)s'
    )


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
    # TODO: See about using np.array here.
    results = []

    create_logger(log_level=level, tag=str(prefix.timestamp))

    start = utcnow()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for key, value in SCHEDULE_TYPES.items():
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

    print("Sim done, execution time: {}".format((utcnow() - start).total_seconds()))


def generate_plots():
    """
    TODO: Implement.  Glob for high pattern in data directory
    then generate dataframes from individual columns with burst lambda
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
