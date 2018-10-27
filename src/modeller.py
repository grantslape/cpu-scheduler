"""Data Modelling class"""
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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

    def write_stats(self, in_list: list, path: str):
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
            writer.writerow(vars(in_list[0]))
            for p in in_list:
                csv_output = (p.id, p.created_at, p.start_at, p.run_time, p.total_time, p.used, p.completed_at)
                writer.writerow(csv_output)
