"""Data Modelling class"""
# pylint: disable=wrong-import-position,wrong-import-order
import csv
import logging
from os import rename
from pathlib import Path
import pandas as pd
import numpy as np
from src.commons.commons import calc_high_level_stats

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class Modeller:
    """
    Data modeller class.  Plots output of simulation runs
    This doesn't really need to be class and could be factored out into
    pure functions
    Attributes:
        abs_path: str root path containing csvs to be plotted
    """
    ABS_PATH = 'data'
    DATA_PATH = 'raw_data'
    PLOT_PATH = 'plots'

    def __init__(self, path: str = ABS_PATH):
        self.abs_path = path

    @staticmethod
    def get_data_path(identifier: str) -> Path:
        """Get data path given identifier"""
        return Path('{0}/{1}/{2}'.format(Modeller.ABS_PATH, identifier, Modeller.DATA_PATH))

    @staticmethod
    def get_plot_path(identifier: str) -> Path:
        """Get plot path given identifier"""
        return Path('{0}/{1}/{2}'.format(Modeller.ABS_PATH, identifier, Modeller.PLOT_PATH))

    def write_stats(self, in_list: np.array, path: str, **kwargs) -> Path:
        """
        Write raw process run statistics
        TODO: In an ideal world there would not be so many magic strings here
        :param in_list: list of processes to be written
        :param path: str: tag name of run to be written
        :return: path to parent of data folder
        """
        timestamp = kwargs.get('created_at')
        members = (self.abs_path, timestamp, Modeller.DATA_PATH, path)
        identifier = "{0}/{1}/{2}/{3}.csv".format(*members)
        data_path = Path(identifier)
        high_level_path = '{}/high_{}.csv'.format(self.get_data_path(timestamp), path)

        with open(str(data_path), 'w', newline='') as file:
            kwargs['turnaround_time'] = 0
            kwargs['wait_time'] = 0
            writer = csv.writer(file, delimiter=',')
            # Write CSV Headers
            writer.writerow((
                'id',
                'created_at',
                'start_at',
                'run_time',
                'total_time',
                'used',
                'completed_at'
            ))
            # Write row for each process
            for p in in_list:
                kwargs['turnaround_time'] += p.total_time
                kwargs['wait_time'] += p.total_time - p.used

                csv_output = (
                    p.id,
                    p.created_at,
                    p.start_at,
                    p.run_time,
                    p.total_time,
                    p.used,
                    p.completed_at
                )
                writer.writerow(csv_output)

            row = calc_high_level_stats(**kwargs)
            with open(high_level_path, 'w', newline='') as high:
                writer = csv.writer(high)
                writer.writerow(
                    ('type',
                     'lambda',
                     'turnaround_time',
                     'throughput',
                     'utilization',
                     'avg_process_count')
                )
                writer.writerow(row)

        if not data_path.exists():
            message = 'Bad stats path: {}'.format(str(identifier))
            logging.critical(message)
            raise Exception(message)

        return Path(high_level_path).parent

    @staticmethod
    def plot(files: [Path]):
        """
        This is a mess, but read through all the high level stats csvs,
        then sort the resultant dataframe by schedule type and lambda value
        plot throughput, turnaround time, utilization, mean.
        Plot this and save to a file.
        :param files: A list of Paths to high level stats to be plotted
        """
        # Read data
        data = pd.concat((pd.read_csv(str(file)) for file in files))
        data = data.sort_values(['type', 'lambda'])

        # Create plots
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12.8, 9.6))
        turnaround, throughput, utilization, mean = axes.flatten()

        # Plot data by type and given statistics
        for key, group in data.groupby(['type']):
            turnaround = group.plot(ax=turnaround,
                                    marker='o',
                                    x='lambda',
                                    y='turnaround_time',
                                    label=key)
            throughput = group.plot(ax=throughput,
                                    marker='o',
                                    x='lambda',
                                    y='throughput',
                                    label=key)
            utilization = group.plot(ax=utilization,
                                     marker='o',
                                     x='lambda',
                                     y='utilization',
                                     label=key)
            mean = group.plot(ax=mean,
                              marker='o',
                              x='lambda',
                              y='avg_process_count',
                              label=key)

        # Format and label individual plots
        turnaround.set_title('Turnaround time')
        throughput.set_title('Throughput')
        utilization.set_title('Utilization')
        mean.set_title('Avg processes in queue')

        throughput.set_ylabel('$processes/second$')
        turnaround.set_ylabel('$seconds$')
        utilization.set_ylabel('$value$')
        mean.set_ylabel('$processes$')

        throughput.yaxis.set_label_position('right')
        mean.yaxis.set_label_position('right')
        throughput.yaxis.tick_right()
        mean.yaxis.tick_right()

        # Final formatting for all plots
        for ax in fig.axes:
            ax.set_xlim(0, 30)
            ax.set_xlabel('$lambda$')
            ax.tick_params(axis='x', which='minor')
            ax.grid(True)
            ax.xaxis.grid(True, which='minor')

        # Save figure and move into data/{tag}/plots/plot.png
        fig.tight_layout()
        plt.savefig('ax')
        members = (files[0].parent.parent, Modeller.PLOT_PATH)
        identifier = "{0}/{1}/plot.png".format(*members)
        rename('ax.png', identifier)
