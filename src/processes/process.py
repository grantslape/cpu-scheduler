"""Process"""

from arrow import Arrow, utcnow


class Process:
    """
    An individual Process
    Attributes:
        process_id: ID of process - uniqueness must be maintained by user
        created_at: the time the process should be created at
        run_time: in seconds
        total_time: total time taken to execute, inclusive of non run time
        used: total time that has been partially worked on this process
        completed_at: Arrow datetime this process was completed at
    """
    def __init__(self,
                 run_time: float,
                 process_id: int):
        """
        Constructor for Process
        :param run_time: Total runtime of process in seconds
        :param process_id:
        """
        self.id = process_id
        self.created_at = None
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

    def set_completed(self, completed_at: Arrow) -> float:
        """
        Set process as completed
        :param completed_at: datetime of completion
        :return: total_time: seconds
        """
        self.completed_at = completed_at
        self.total_time = (self.completed_at - self.created_at).total_seconds()
        return self.total_time

    def set_used(self, start: Arrow, end: Arrow) -> float:
        """
        Set partial amount of time used
        :param start: Arrow object representing work start time
        :param end: Arrow object representing work end time
        :return: time remaining in sec as float
        """
        elapsed = (end - start).total_seconds()
        self.used += elapsed
        return self.total_time - self.used
