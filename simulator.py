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
    table.loc[:, 'srv beg'] = 0
    table.loc[1, 'arrival t'] = 0
    btw_arrival = rgs.btw_arrival()
    table.loc[:, 'Q t'] = rgs.queue_time()
    table.loc[:, 'corona +'] = rgs.corona()
    table.loc[:, 'srv t'] = rgs.service_time()
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
    corona_len = len(corona_table)
    normal_len = len(normal_table)

    np_corona_table = corona_table.to_numpy()
    np_normal_table = normal_table.to_numpy()
    corona_as_t_idx = [corona_table.columns.get_loc(c) for c in ['arrival t', 'srv t', 'Q t']]
    corona_set_idx = [corona_table.columns.get_loc(c) for c in ['srv beg', 'srv end', 'Q t']]
    normal_set_idx = [normal_table.columns.get_loc(c) for c in ['srv beg', 'srv end', 'Q t']]
    normal_as_t_idx = [normal_table.columns.get_loc(c) for c in ['arrival t', 'srv t', 'Q t']]

    corona_arrival, corona_srv_t, c_Q_t = np_corona_table[corona_idx, corona_as_t_idx]
    normal_arrival, normal_srv_t, n_Q_t = np_normal_table[normal_idx, normal_as_t_idx]
    for _ in range(Conf.CLIENT_NO):
        if corona_idx != corona_len and (
                corona_arrival <= now or corona_arrival <= normal_arrival or normal_idx == normal_len):
            begin = now if corona_arrival < now else corona_arrival
            c_Q_t -= (begin - corona_arrival)
            if c_Q_t >= 0:
                now = end = corona_srv_t + begin
                np_corona_table[corona_idx, corona_set_idx] = begin, end, c_Q_t
            else:
                np_corona_table[corona_idx, 6] = "gone"
            corona_idx += 1
            if corona_idx != corona_len:
                corona_arrival, corona_srv_t, c_Q_t = np_corona_table[corona_idx, corona_as_t_idx]
        else:
            begin = now if normal_arrival < now else normal_arrival
            n_Q_t -= (begin - normal_arrival)
            if n_Q_t >= 0:
                now = end = normal_srv_t + begin
                np_normal_table[normal_idx, normal_set_idx] = begin, end, n_Q_t
            else:
                np_normal_table[normal_idx, 6] = "gone"
            normal_idx += 1
            if normal_idx != normal_len:
                normal_arrival, normal_srv_t, n_Q_t = np_normal_table[normal_idx, normal_as_t_idx]

        # doctor check kone alan bimar(a) doctor_service_finish < now -> take new bimar(b) az saf

        # append new bimar to that saf

    print(corona_len, normal_len)
    print(pd.DataFrame(np_corona_table, columns=Conf.TABLE_COLUMNS), "\n")
    print(pd.DataFrame(np_normal_table, columns=Conf.TABLE_COLUMNS))
    # print(np_corona_table[-5:])
    # print(np_normal_table[-5:])
