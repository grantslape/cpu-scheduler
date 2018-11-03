"""Data Modelling class"""
import csv
import logging
from os import rename
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.commons.commons import calc_high_level_stats


class Modeller:
    """
    Data modeller class.  Plots output of simulation runs

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
            writer.writerow(vars(in_list[0]))
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

    def plot(self, files: [[Path]]):
        """

        :return:
        """
        data = pd.concat((pd.read_csv(str(file)) for file in files))
        data = data.sort_values(['type', 'lambda'])
        # fig, ax = plt.subplots(figsize=(12.8, 9.6))
        fig, ax = plt.subplots(figsize=(12.8, 9.6))

        for key, group in data.groupby(['type']):
            ax = group.plot(ax=ax, kind='line', x='lambda', y='utilization', label=key)

        plt.savefig('ax')
        members = (files[0].parent.parent, Modeller.PLOT_PATH)
        identifier = "{0}/{1}/plot.png".format(*members)
        rename('ax.png', identifier)
