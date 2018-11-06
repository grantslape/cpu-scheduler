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
        format='%(processName)s: %(levelname)s - %(message)s'
    )


def main():
    """CLI Frontent"""
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', type=int, help='Number of trials')
    parser.add_argument('max_rate', type=int, help='max processes per second')
    parser.add_argument('seed', type=int, help='base seed for PRNG. base_seed + rate')
    verbose_help = 'Set Log level to debug.  Will use a lot of disk space'
    parser.add_argument('-v', '--verbose', action='store_true', help=verbose_help)
    parser.add_argument('-o', '--once', action='store_true', help='Run the simulation only once.  Uses special args')
    parser.add_argument('--type', type=int, required=False, help='scheduler type [1-3]')
    parser.add_argument('--service_time', type=float, required=False, help='average svc time')
    parser.add_argument('--quantum', type=float, required=False, help='quantum value (sec)')
    args = parser.parse_args()

    start = utcnow()
    length = args.runs
    rates = [i + 1 for i in range(args.max_rate)]
    results = []

    # Configure Logger
    level = logging.DEBUG if args.verbose else logging.INFO
    create_logger(log_level=level, tag=str(start.timestamp))

    if args.once:
        results.append(run_once(args, start))
    else:

        print('Sim running, please be patient')
        # Use a process pool to run simulations simultaneously
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for key, value in SCHEDULE_TYPES.items():
                kwargs = {
                    'method': value,
                    'prefix': start,
                    'quantum': 0.01,
                    'rate': None,
                    'length': length
                }

                for rate in rates:
                    # This ensures a consistent seed is used across schedule methods
                    np.random.seed(int(str(args.seed) + str(rate)))
                    kwargs['rate'] = rate
                    results.append(executor.submit(run_sim, **kwargs))

                # Run everything again for RR with the second quantum value
                if key == 'RR':
                    kwargs['quantum'] = 0.2
                    for rate in rates:
                        np.random.seed(int(str(args.seed) + str(rate)))
                        kwargs['rate'] = rate
                        results.append(executor.submit(run_sim, **kwargs))

    # Get the path to high level stats and plot them
    if not args.once:
        data = results[0].result()
        generate_plots(data)
        print('Plot is at {}/plots/plot.png'.format(str(data.parent)))

    message = "Sim done, execution time: {}".format((utcnow() - start).total_seconds())
    print(message)
    logging.info(message)


def generate_plots(path: Path):
    """
    generate dataframes from individual columns with burst lambda
    :param: path: Path to stats directory
    """
    runs = list(path.glob('**/high*.csv'))
    Modeller.plot(runs)


def run_sim(method: int,
            prefix: Arrow,
            rate: int,
            length: int,
            quantum: float = None) -> Path:
    """
    run sim with given parameters
    :param method: scheduler method from commons.SCHEDULE_TYPES
    :param prefix: folder prefix for data, usually unix timestamp
    :param rate: rate of process arrival
    :param length: length of simulation in processes
    :param quantum: time quantum (only for round robin)
    :return: Path to high level stats
    """
    return Simulator(
        method=method,
        created_at=prefix,
        quantum=quantum,
        process_rate=rate,
        length=length
    ).run()


def run_once(args, start: Arrow) -> Path:
    """Run simulation once with given values"""
    members = (args.type, args.max_rate, args.service_time, args.quantum)
    message = 'Running Sim with values\nType:\t{0}\nRate\t{1}\nService Time\t{2}\nQuantum\t{3}'.format(*members)
    logging.info(message)
    print(message)

    return run_sim(method=args.type, prefix=start, quantum=args.quantum, rate=args.max_rate, length=args.runs)


if __name__ == '__main__':
    main()
