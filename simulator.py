import pandas as pd
import numpy as np

from conf import Conf
import random_generators as rgs


if __name__ == '__main__':

    # initialization
    table = pd.DataFrame(index=list(range(1, Conf.CLIENT_NO + 1)), columns=Conf.TABLE_COLUMNS)
    table.loc[1, 'arrival time'] = 0
    table.loc[:, 'service time'] = rgs.service_time()
    table.loc[:, 'corona +'] = rgs.corona()
    table.loc[:, 'time between arrivals'] = rgs.btw_arrival()
