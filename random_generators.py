import numpy as np

from conf import Conf


def btw_arrival():
    return np.random.exponential(scale=1/Conf.LAMBDA, size=Conf.CLIENT_NO)


def service_time():
    return np.random.exponential(scale=1/Conf.MU, size=Conf.CLIENT_NO)


def visit_time(mean_visit_time):
    return np.random.exponential(scale=mean_visit_time, size=Conf.CLIENT_NO)    # fixme Number of random numbers that should be returned


def queue_time():
    return np.random.uniform(1, 5, Conf.CLIENT_NO)  # fixme should it be 20?


def corona():
    return np.random.choice([True, False], size=Conf.CLIENT_NO, p=[0.1, 0.9])
