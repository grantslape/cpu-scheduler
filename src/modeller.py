"""Data Modelling class"""
import csv
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import rename

from src.process import Process
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
        :return: data_path: base Path to stats folder
        """
        timestamp = kwargs.get('created_at')
        members = (self.abs_path, timestamp, Modeller.DATA_PATH, path)
        identifier = "{0}/{1}/{2}/{3}.csv".format(*members)
        data_path = Path(identifier)

        with open(str(data_path), 'w', newline='') as file:
            kwargs['turnaround_time'] = 0
            kwargs['wait_time'] = 0
            writer = csv.writer(file, delimiter=',')
            # Write CSV Headers
            writer.writerow(vars(in_list[0]))
            # Write row for each process
            for p in in_list:
                # TODO: leverage numpy array column summing
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
            with open('{}/high_{}.csv'.format(self.get_data_path(timestamp), path), 'w', newline='') as high:
                writer = csv.writer(high)
                writer.writerow(('turnaround_time', 'throughput', 'utilization', 'avg_process_count'))
                writer.writerow(row)

        if not data_path.exists():
            message = 'Bad stats path: {}'.format(str(identifier))
            logging.critical(message)
            raise Exception(message)

        return data_path

    def plot(self, path: str, name: str):
        """
        Example of plotting a given CSV
        :param path: path to CSV to be plotted
        :param name: name of csv
        :return:
        """
        # TODO: THIS IS COOL AND ALL BUT WE NEED TO PLOT LAMBDA AS X
        # AND HAVE 4 PLOTS FOR EACH OF THE FOLLOWING METRICS AS Y:
        # 1) AVERAGE TURNAROUND TIME
        # 2) TOTAL THROUGHPUT
        # 3) CPU UTILIZATION
        # 4) AVERAGE # OF PROCESSES IN READY QUEUE (SEE EMAIL)
        # Different color line for each of the scheduler types (RR twice)
        data = pd.read_csv('{0}.csv'.format(path))
        data.sort_values('id')
        data.plot(x='id', y='total_time', kind='bar')
        plt.savefig('ax')
        members = (self.abs_path, self.created_at, Modeller.PLOT_PATH, name)
        identifier = "{0}/{1}/{2}/{3}.png".format(*members)
        rename('ax.png', identifier)
