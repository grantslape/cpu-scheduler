"""Helper Functions"""
import numpy as np

SCHEDULE_TYPES = {
    'FCFS': 1,
    'SJF': 2,
    'RR': 3
}

EVENT_TYPES = {
    'NEW': 1,
    'COMPLETE': 2,
    'SWITCH': 3
}


def rand_exp_float(given_lambda: float) -> float:
    """
    Generate a random number that follows an exponential distribution
    :param given_lambda: lambda for exponential distribution
    :return psuedorandom number following exp distribution
    """
    if given_lambda > 1:
        given_lambda = 1/given_lambda
    return np.random.exponential(scale=given_lambda)


def calc_high_level_stats(turnaround_time: float,
                          wait_time: float,
                          length: int,
                          usage: float,
                          total_time: float,
                          given_lambda: int,
                          **kwargs):
    """
    Write high level stats
    # 1) AVERAGE TURNAROUND TIME
    # 2) TOTAL THROUGHPUT
    # 3) CPU UTILIZATION
    # 4) AVERAGE # OF PROCESSES IN READY QUEUE (SEE EMAIL)
    :param turnaround_time:
    :param wait_time:
    :param length:
    :param usage:
    :param total_time:
    :param given_lambda:
    :return:
    """
    utilization = usage / total_time
    throughput = length / total_time
    schedule_type = kwargs.get('type')
    # Hack for now to support plotting
    if schedule_type == SCHEDULE_TYPES['RR'] and kwargs.get('quantum') > 0.01:
        schedule_type = 4

    return (schedule_type,
            given_lambda,
            turnaround_time / length,
            throughput,
            utilization,
            (1/given_lambda) * wait_time)
