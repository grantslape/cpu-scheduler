"""Helper Functions"""
from datetime import timedelta
from math import log
from random import randint

from src.commons.settings import settings as sf


def convert_td(delta: timedelta) -> int:
    """
    DEPRECATED
    Convert a timedelta to milliseconds rounded to nearest int
    :param delta: timedelta to be converted
    :return: td in milliseconds as integer
    """
    return int(delta.total_seconds() * sf['SEC_TO_MILLI'])


def rand_exp_float(given_lambda: float) -> float:
    """
    Generate a random number that follows an exponential distribution
    :param given_lambda: lambda for exponential distribution
    :return x: random number following exp distribution
    """
    u = x = 0
    while u == 0:
        u = randint(sf['RAND_MIN'], sf['RAND_MAX']) / sf['RAND_MAX']
        x = (-1 / given_lambda) * log(u)

    return x
