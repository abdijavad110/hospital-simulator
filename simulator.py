from collections import deque

import pandas as pd
import numpy as np
import math
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


def get_col_idx(name):
    return Conf.TABLE_COLUMNS.index(name)


def check_free_doctor(np_normal_table, np_corona_table, p_index, p_has_corona, visit_queues, room_queues_length,
                      arrive_time, visiting_patients):
    min_room_length = math.inf
    min_room_length_idx = 0
    for room_idx in range(len(Conf.DOCTORS)):
        for doc_idx in range(len(Conf.DOCTORS[room_idx])):

            while True:
                last_visit_end = None
                if visiting_patients[room_idx][doc_idx] is not None:
                    last_visit_end = visiting_patients[room_idx][doc_idx][get_col_idx("visit end")]
                    if last_visit_end <= arrive_time:
                        room_queues_length[room_idx] -= 1
                        visiting_patients[room_idx][doc_idx] = None
                    else:
                        break

                corona_queue = visit_queues[room_idx][0]
                normal_queue = visit_queues[room_idx][1]

                if len(corona_queue) > 0 and len(normal_queue) > 0:
                    if last_visit_end:
                        if corona_queue[0][get_col_idx('srv end')] <= normal_queue[0][get_col_idx('srv end')]:
                            visiting_patients[room_idx][doc_idx] = corona_queue[0]
                            corona_queue.popleft()
                        elif corona_queue[0][get_col_idx('srv end')] <= last_visit_end:
                            visiting_patients[room_idx][doc_idx] = corona_queue[0]
                            corona_queue.popleft()
                        else:
                            visiting_patients[room_idx][doc_idx] = normal_queue[0]
                            normal_queue.popleft()

                    else:
                        if corona_queue[0][get_col_idx('srv end')] <= normal_queue[0][get_col_idx('srv end')]:
                            visiting_patients[room_idx][doc_idx] = corona_queue[0]
                            corona_queue.popleft()

                        else:
                            visiting_patients[room_idx][doc_idx] = normal_queue[0]
                            normal_queue.popleft()
                elif len(corona_queue) > 0 and len(normal_queue) == 0:
                    visiting_patients[room_idx][doc_idx] = corona_queue[0]
                elif len(corona_queue) == 0 and len(normal_queue) > 0:
                    visiting_patients[room_idx][doc_idx] = normal_queue[0]
                    normal_queue.popleft()
                else:
                    break

                visiting_srv_end = visiting_patients[room_idx][doc_idx][get_col_idx('srv end')]
                if last_visit_end and last_visit_end > visiting_srv_end:
                    visit_start=last_visit_end
                else:
                    visit_start=visiting_srv_end

                visiting_patients[room_idx][doc_idx][get_col_idx('visit beg')] = visit_start
                visit_time = rgs.visit_time(Conf.DOCTORS[room_idx][doc_idx])
                visiting_patients[room_idx][doc_idx][get_col_idx('visit t')] = visit_time
                visiting_patients[room_idx][doc_idx][get_col_idx('visit end')] = visit_start + visit_time

            if min_room_length > room_queues_length[room_idx]:
                min_room_length = room_queues_length[room_idx]
                min_room_length_idx = room_idx

    if p_has_corona:
        p = np_corona_table[p_index]
        visit_queues[min_room_length_idx][0].append(p)
        room_queues_length[min_room_length_idx] += 1
    else:
        p = np_normal_table[p_index]
        visit_queues[min_room_length_idx][1].append(p)
        room_queues_length[min_room_length_idx] += 1


def number_of_doctors(doctors):
    num_docs = 0
    for m in doctors: num_docs += len(m)
    return num_docs


if __name__ == '__main__':
    # initialization
    init_pd()
    raw_table = raw_table()
    corona_table = raw_table.loc[raw_table['corona +']].reset_index(drop=True)
    normal_table = raw_table.loc[~ raw_table['corona +']].reset_index(drop=True)
    visiting_patients = [[None] * len(Conf.DOCTORS[i]) for i in range(len(Conf.DOCTORS))]
    visit_queues = [[deque(), deque()] for i in range(len(Conf.DOCTORS))]
    room_queues_length = [0 for i in range(len(Conf.DOCTORS))]

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
            p_index = corona_idx
            p_has_corona = True
            begin = now if corona_arrival < now else corona_arrival
            c_Q_t -= (begin - corona_arrival)
            if c_Q_t >= 0:
                now = end = corona_srv_t + begin
                np_corona_table[corona_idx, corona_set_idx] = begin, end, c_Q_t
            else:
                now = end = corona_srv_t + begin
                np_corona_table[corona_idx, corona_set_idx] = begin, end, c_Q_t
                # np_corona_table[corona_idx, 6] = "gone"
            corona_idx += 1
            if corona_idx != corona_len:
                corona_arrival, corona_srv_t, c_Q_t = np_corona_table[corona_idx, corona_as_t_idx]
        else:
            p_index = normal_idx
            p_has_corona = False
            begin = now if normal_arrival < now else normal_arrival
            n_Q_t -= (begin - normal_arrival)
            if n_Q_t >= 0:
                now = end = normal_srv_t + begin
                np_normal_table[normal_idx, normal_set_idx] = begin, end, n_Q_t
            else:
                now = end = normal_srv_t + begin
                np_normal_table[normal_idx, normal_set_idx] = begin, end, n_Q_t
                # np_normal_table[normal_idx, 6] = "gone"
            normal_idx += 1
            if normal_idx != normal_len:
                normal_arrival, normal_srv_t, n_Q_t = np_normal_table[normal_idx, normal_as_t_idx]

        # doctor check kone alan bimar(a) doctor_service_finish < now -> take new bimar(b) az saf
        check_free_doctor(np_normal_table, np_corona_table, p_index, p_has_corona, visit_queues, room_queues_length,
                          now, visiting_patients)
        # append new bimar to that saf

    print(corona_len, normal_len)
    print(pd.DataFrame(np_corona_table, columns=Conf.TABLE_COLUMNS), "\n")
    print(pd.DataFrame(np_normal_table, columns=Conf.TABLE_COLUMNS))
    # print(np_corona_table[-5:])
    # print(np_normal_table[-5:])
