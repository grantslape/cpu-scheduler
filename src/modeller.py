"""Data Modelling class"""
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import rename

from src.process import Process


class Modeller:
    """
    Data modeller class.  Plots output of simulation runs

    Attributes:
        abs_path: str root path containing csvs to be plotted
        created_at: Unix timestamp used as folder prefix
    """
    DATA_PATH = 'raw_data'
    PLOT_PATH = 'plots'

    def __init__(self, path: str, created_at: int):
        self.abs_path = path
        self.created_at = created_at

    def write_stats(self, in_list: [Process], path: str):
        """
        Write raw process run statistics
        :param in_list: list of processes to be written
        :param path: tag name of run to be written
        :return: TODO: maybe a path reference to file?
        """
        members = (self.abs_path, self.created_at, Modeller.DATA_PATH, path)
        identifier = "{0}/{1}/{2}/{3}.csv".format(*members)

        with open(identifier, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            # Write CSV Headers
            writer.writerow(vars(in_list[0]))
            # Write row for each process
            for p in in_list:
                csv_output = (p.id,
                              p.created_at,
                              p.start_at,
                              p.run_time,
                              p.total_time,
                              p.used,
                              p.completed_at)
                writer.writerow(csv_output)

        return '{0}/{1}/{2}/{3}'.format(*members), path

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
