"""Process"""
import arrow
from arrow import Arrow


class Process:
    def __init__(self,
                 activate_at: Arrow = arrow.utcnow(),
                 total_time: int = 60):
        """
        Constructor for Process
        :param activate_at: The time the process should activate at
        :param total_time: Total runtime of process in milliseconds
        """
        self.created_at = activate_at
        self.total_time = total_time
        self.used = None
        self.completed_at = None

    def set_completed(self, completed_at: Arrow) -> int:
        """
        Set process as completed
        :param completed_at: datetime of completion
        :return:
        """
        self.completed_at = completed_at
        self.total_time = self.completed_at - self.created_at
        return self.total_time

    def set_used(self, partial: int):
        """
        Set
        :param partial:
        :return:
        """
