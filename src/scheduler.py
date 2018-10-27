"""Scheduler with baked in algorithm"""
import weakref


class Scheduler:
    """
    Scheduler for Simulation.

    Algorithm to use for scheduling is baked into each scheduler to abstract
    away switch statements.

    Attributes:
        parent: reference to the parent simulator
        method: type of scheduling algorithm to use as enumerated in
            Scheduler.Types

    """
    Types = {
        'FCFS': 1,
        'SJF': 2,
        'RR': 3
    }

    def __init__(self, parent, method: int):
        self.parent = weakref.ref(parent)
        self.type = method
