import numpy as np

from conf import Conf


def btw_arrival():
    return np.random.exponential(scale=1/Conf.LAMBDA, size=Conf.CLIENT_NO)


def service_time():
    return np.random.exponential(scale=1/Conf.MU, size=Conf.CLIENT_NO)


def visit_time(visit_lambda):
    return np.random.exponential(scale=1/visit_lambda, size=1)[0]


def queue_time():
    return Conf.ALPHA


def corona():
    return np.random.choice([True, False], size=Conf.CLIENT_NO, p=[0.1, 0.9])
