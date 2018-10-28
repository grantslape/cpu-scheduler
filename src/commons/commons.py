"""Helper Functions"""
import numpy as np


def rand_exp_float(given_lambda: float) -> float:
    """
    Generate a random number that follows an exponential distribution
    :param given_lambda: lambda for exponential distribution
    :return psuedorandom number following exp distribution
    """
    if given_lambda > 1:
        given_lambda = 1/given_lambda
    return np.random.exponential(scale=given_lambda)
