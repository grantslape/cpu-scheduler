"""Helper Functions"""
from datetime import timedelta


def convert_td(delta: timedelta) -> int:
    """
    Convert a timedelta to milliseconds rounded to nearest int
    :param delta: timedelta to be converted
    :return: td in milliseconds as integer
    """
    return int(delta.total_seconds() * 1000)
