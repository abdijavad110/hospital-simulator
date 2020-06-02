import numpy as np

from conf import Conf


def btw_arrival():
    return np.random.uniform(1, 10, Conf.CLIENT_NO)  # fixme poisson with mean Conf.LAMBDA and size of Conf.CLIENT_NO


def service_time():
    return np.random.uniform(1, 10, Conf.CLIENT_NO)  # fixme poisson with mean Conf.MU and size of Conf.CLIENT_NO


def corona():
    return np.random.choice([True, False], size=Conf.CLIENT_NO, p=[0.1, 0.9])
