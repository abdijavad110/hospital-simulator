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
    table.loc[:, 'srv beg'] = 0
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
    corona_table = raw_table.loc[raw_table['corona +']].reset_index(drop=True)
    normal_table = raw_table.loc[~ raw_table['corona +']].reset_index(drop=True)

    now = 0
    corona_idx = 0
    normal_idx = 0
    for _ in range(Conf.CLIENT_NO):
        corona_arrival, corona_srv_t = corona_table.loc[corona_idx, ['arrival t', 'srv t']]
        normal_arrival, normal_srv_t = normal_table.loc[normal_idx, ['arrival t', 'srv t']]
        if corona_arrival <= now or corona_arrival <= normal_arrival:
            begin = now if corona_arrival < now else corona_arrival
            now = end = corona_srv_t + begin
            Q_t = begin - corona_arrival
            corona_table.loc[corona_idx, ['srv beg', 'srv end', 'Q t']] = begin, end, Q_t
            corona_idx += 1
            if corona_idx == len(corona_table):
                for i in range(normal_idx, len(normal_table)):
                    arrival, srv_t = normal_table.loc[i, ['arrival t', 'srv t']]
                    begin = now if arrival < now else arrival
                    now = end = srv_t + begin
                    Q_t = begin - arrival
                    normal_table.loc[i, ['srv beg', 'srv end', 'Q t']] = begin, end, Q_t
                break
        else:
            begin = now if normal_arrival < now else normal_arrival
            now = end = normal_srv_t + begin
            Q_t = begin - normal_arrival
            normal_table.loc[normal_idx, ['srv beg', 'srv end', 'Q t']] = begin, end, Q_t
            normal_idx += 1
            if normal_idx == len(normal_table):
                for i in range(corona_idx, len(corona_table)):
                    arrival, srv_t = corona_table.loc[i, ['arrival t', 'srv t']]
                    begin = now if arrival < now else arrival
                    now = end = srv_t + begin
                    Q_t = begin - arrival
                    corona_table.loc[i, ['srv beg', 'srv end', 'Q t']] = begin, end, Q_t
                break

    print(len(corona_table), len(normal_table))
    print(corona_table.tail())
    print(normal_table.tail())
