"""Data Modelling class"""
import numpy as np
import matplotlib.pyplot as plt


class Modeller:
    """
    Data modeller class.  Plots output of simulation runs

    Attributes:
        abs_path: str root path containing csvs to be plotted
    """
    def __init__(self, path: str):
        self.abs_path = path

    def write_stats(self, processes: list):
        """Write run statistics"""
        # TODO: CSV WRITER
        pass
