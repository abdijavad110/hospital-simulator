import pandas as pd
import numpy as np

from conf import Conf
import random_generators as rgs


def init_pd():
    pd.set_option('precision', 2)
    pd.set_option('max_columns', 20)
    pd.set_option('display.expand_frame_repr', False)


def raw_table():
    table = pd.DataFrame(index=list(range(1, Conf.CLIENT_NO + 1)), columns=Conf.TABLE_COLUMNS)
    table.loc[1, 'arrival t'] = 0
    table.loc[1, 'srv begin'] = 0
    table.loc[:, 'srv t'] = rgs.service_time()
    table.loc[:, 'corona +'] = rgs.corona()
    btw_arrival = rgs.btw_arrival()
    btw_arrival[0] = 0
    table.loc[:, 't btw arrival'] = btw_arrival
    table.loc[:, 'arrival t'] = np.cumsum(btw_arrival)
    return table


if __name__ == '__main__':
    # initialization
    init_pd()
    raw_table = raw_table()
    corona_table = raw_table.loc[raw_table['corona +']]
    normal_table = raw_table.loc[~ raw_table['corona +']]


    print(len(corona_table), len(normal_table))
    print(corona_table.tail())
    print(normal_table.tail())
