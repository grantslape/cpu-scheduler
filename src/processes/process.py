"""Process"""

from arrow import Arrow, utcnow

from src.helpers.timedeltas import convert_td


class Process:
    """
    An individual Process
    Attributes:
        created_at: the time the process should be created at
        run_time: in milliseconds
        total_time: total time taken to execute, inclusive of non run time
        used: total time that has been partially worked on this process
        completed_at: Arrow datetime this process was completed at
    """
    def __init__(self,
                 activate_at: Arrow = utcnow(),
                 run_time: int = 60):
        """
        Constructor for Process
        :param activate_at: The time the process should activate at
        :param run_time: Total runtime of process in milliseconds
        """
        self.created_at = activate_at
        self.run_time = run_time
        self.total_time = None
        self.used = None
        self.completed_at = None

    def __lt__(self, other):
        """Implement comparable"""
        priority = (self.created_at,
                    self.run_time - self.used,
                    self.run_time)
        other_priority = (other.created_at,
                          other.run_time - other.used,
                          other.run_time)
        return priority < other_priority

    def set_completed(self, completed_at: Arrow) -> int:
        """
        Set process as completed
        :param completed_at: datetime of completion
        :return: total_time: int representing milliseconds
        """
        self.completed_at = completed_at
        self.total_time = convert_td(self.completed_at - self.created_at)
        return self.total_time

    def set_used(self, start: Arrow, end: Arrow) -> int:
        """
        Set partial amount of time used
        :param start: Arrow object representing work start time
        :param end: Arrow object representing work end time
        :return: time remaining in ms as int
        """
        elapsed = convert_td(end - start)
        self.used += elapsed
        return self.total_time - self.used
