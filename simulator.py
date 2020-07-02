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

    np_corona_table = corona_table.to_numpy()
    np_normal_table = normal_table.to_numpy()
    corona_as_t_idx = [corona_table.columns.get_loc(c) for c in ['arrival t', 'srv t']]
    corona_set_idx = [corona_table.columns.get_loc(c) for c in ['srv beg', 'srv end', 'Q t']]
    normal_set_idx = [normal_table.columns.get_loc(c) for c in ['srv beg', 'srv end', 'Q t']]
    normal_as_t_idx = [normal_table.columns.get_loc(c) for c in ['arrival t', 'srv t']]
    # 10 seconds until reaching this point fo 10M clients

    corona_arrival, corona_srv_t = np_corona_table[corona_idx, corona_as_t_idx]
    normal_arrival, normal_srv_t = np_normal_table[normal_idx, normal_as_t_idx]
    for _ in range(Conf.CLIENT_NO):
        if corona_arrival <= now or corona_arrival <= normal_arrival:
            begin = now if corona_arrival < now else corona_arrival
            now = end = corona_srv_t + begin
            Q_t = begin - corona_arrival
            np_corona_table[corona_idx, corona_set_idx] = begin, end, Q_t
            corona_idx += 1
            if corona_idx == len(corona_table):
                for i in range(normal_idx, len(normal_table)):
                    arrival, srv_t = np_normal_table[i, normal_as_t_idx]
                    begin = now if arrival < now else arrival
                    now = end = srv_t + begin
                    Q_t = begin - arrival
                    np_normal_table[i, normal_set_idx] = begin, end, Q_t
                break
            corona_arrival, corona_srv_t = np_corona_table[corona_idx, corona_as_t_idx]
        else:
            begin = now if normal_arrival < now else normal_arrival
            now = end = normal_srv_t + begin
            Q_t = begin - normal_arrival
            np_normal_table[normal_idx, normal_set_idx] = begin, end, Q_t
            normal_idx += 1
            if normal_idx == len(normal_table):
                for i in range(corona_idx, len(corona_table)):
                    arrival, srv_t = np_corona_table[i, corona_as_t_idx]
                    begin = now if arrival < now else arrival
                    now = end = srv_t + begin
                    Q_t = begin - arrival
                    np_corona_table[i, corona_set_idx] = begin, end, Q_t
                break
            normal_arrival, normal_srv_t = np_normal_table[normal_idx, normal_as_t_idx]

    print(len(corona_table), len(normal_table))
    print(pd.DataFrame(np_corona_table, columns=Conf.TABLE_COLUMNS), "\n")
    print(pd.DataFrame(np_normal_table, columns=Conf.TABLE_COLUMNS))
    # print(np_corona_table[-5:])
    # print(np_normal_table[-5:])
