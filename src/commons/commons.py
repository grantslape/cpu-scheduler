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
    :return pseudo-random number following exp distribution
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
    # 4) AVERAGE # OF PROCESSES IN READY QUEUE
    :param turnaround_time: Total Run time / Number of Processes
    :param wait_time: Total wait time of all processes
    :param length: Number of Processes
    :param usage: Total CPU usage in seconds
    :param total_time: Total simulation time in seconds
    :param given_lambda: process arrival rate
    :return: tuple to be written to csv
    """
    utilization = usage / total_time
    throughput = length / total_time
    int_schedule_type = kwargs.get('type')
    if int_schedule_type == SCHEDULE_TYPES['FCFS']:
        schedule_type = 'First Come First Served'
    elif int_schedule_type == SCHEDULE_TYPES['SJF']:
        schedule_type = 'Shortest Job First'
    elif int_schedule_type == SCHEDULE_TYPES['RR'] and kwargs.get('quantum') == 0.01:
        schedule_type = 'Round Robin 0.01'
    elif int_schedule_type == SCHEDULE_TYPES['RR'] and kwargs.get('quantum') == 0.2:
        schedule_type = 'Round Robin 0.2'
    else:
        schedule_type = 'Unknown'

    return (schedule_type,
            given_lambda,
            turnaround_time / length,
            throughput,
            utilization,
            (1/given_lambda) * wait_time)
