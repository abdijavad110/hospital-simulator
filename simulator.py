import math
import warnings
import numpy as np
import pandas as pd
from collections import deque
import matplotlib.pyplot as plt

import random_generators as rgs
from conf import Conf, init_conf

warnings.simplefilter(action='ignore', category=Warning)


def init_pd():
    pd.set_option('precision', 3)
    pd.set_option('max_columns', 20)
    pd.set_option('display.expand_frame_repr', False)


def raw_table():
    table = pd.DataFrame(index=list(range(1, Conf.CLIENT_NO + 1)), columns=Conf.TABLE_COLUMNS)
    table.loc[:, 'srv beg'] = 0
    table.loc[1, 'arrival_t'] = 0
    btw_arrival = rgs.btw_arrival()
    patience = rgs.queue_time()
    table.loc[:, 'remaining_P'] = patience
    table.loc[:, 'init_patience'] = patience
    table.loc[:, 'corona'] = rgs.corona()
    table.loc[:, 'srv_t'] = rgs.service_time()
    btw_arrival[0] = 0
    table.loc[:, 't btw arrival'] = btw_arrival
    table.loc[:, 'arrival_t'] = np.cumsum(btw_arrival)
    return table


def get_col_idx(name):
    return Conf.TABLE_COLUMNS.index(name)


def check_patient_is_tired(patient, last_visit_end=None):
    # visiting_srv_end = patient[get_col_idx('srv_end')]
    visiting_srv_end = patient[5]
    if last_visit_end and last_visit_end > visiting_srv_end:
        visit_start = last_visit_end
    else:
        visit_start = visiting_srv_end

    delay = visit_start - visiting_srv_end
    # patient[get_col_idx('remaining_P')] -= delay
    patient[6] -= delay

    # if patient[get_col_idx('remaining_P')] < 0:
    if patient[6] < 0:
        patient[6] = "gone"
        return True
    return False


def pop_tired_patients(corona_queue, normal_queue, last_visit_end):
    go = True
    count = 0
    while go:
        go = False

        if len(corona_queue) > 0 and check_patient_is_tired(corona_queue[0], last_visit_end):
            corona_queue.popleft()
            count += 1
            go = True
        if len(normal_queue) > 0 and check_patient_is_tired(normal_queue[0], last_visit_end):
            normal_queue.popleft()
            count += 1
            go = True
    return count


def flush_patients(visit_queues, room_queues_length,
                   visiting_patients, arrive_time=None):
    min_room_length = math.inf
    min_room_length_idx = 0
    for room_idx in range(len(Conf.DOCTORS)):
        while True:
            min_visit_end = 1e20
            min_doctor_idx = 0

            for doc_idx in range(len(Conf.DOCTORS[room_idx])):
                last_visit_end = -1e20
                if visiting_patients[room_idx][doc_idx] is not None:
                    # last_visit_end = visiting_patients[room_idx][doc_idx][get_col_idx("visit_end")]
                    last_visit_end = visiting_patients[room_idx][doc_idx][9]
                if arrive_time:
                    if last_visit_end <= arrive_time:
                        if last_visit_end < min_visit_end:
                            min_visit_end = last_visit_end
                            min_doctor_idx = doc_idx
                else:
                    if last_visit_end < min_visit_end:
                        min_visit_end = last_visit_end
                        min_doctor_idx = doc_idx
            if arrive_time and min_visit_end == 1e20:
                break
            if min_visit_end == -1e20:
                min_visit_end = None

            visiting_patients[room_idx][min_doctor_idx] = None

            corona_queue = visit_queues[room_idx][0]
            normal_queue = visit_queues[room_idx][1]

            left_ones = pop_tired_patients(corona_queue, normal_queue, min_visit_end)
            room_queues_length[room_idx] -= left_ones

            if len(corona_queue) > 0 and len(normal_queue) > 0:
                if min_visit_end:
                    # if corona_queue[0][get_col_idx('srv_end')] <= normal_queue[0][get_col_idx('srv_end')]:
                    if corona_queue[0][5] <= normal_queue[0][5]:
                        visiting_patients[room_idx][min_doctor_idx] = corona_queue[0]
                        corona_queue.popleft()
                    # elif corona_queue[0][get_col_idx('srv_end')] <= min_visit_end:
                    elif corona_queue[0][5] <= min_visit_end:
                        visiting_patients[room_idx][min_doctor_idx] = corona_queue[0]
                        corona_queue.popleft()
                    else:
                        visiting_patients[room_idx][min_doctor_idx] = normal_queue[0]
                        normal_queue.popleft()
                else:
                    # if corona_queue[0][get_col_idx('srv_end')] <= normal_queue[0][get_col_idx('srv_end')]:
                    if corona_queue[0][5] <= normal_queue[0][5]:
                        visiting_patients[room_idx][min_doctor_idx] = corona_queue[0]
                        corona_queue.popleft()

                    else:
                        visiting_patients[room_idx][min_doctor_idx] = normal_queue[0]
                        normal_queue.popleft()
            elif len(corona_queue) > 0 and len(normal_queue) == 0:

                visiting_patients[room_idx][min_doctor_idx] = corona_queue[0]
                corona_queue.popleft()

            elif len(corona_queue) == 0 and len(normal_queue) > 0:

                visiting_patients[room_idx][min_doctor_idx] = normal_queue[0]
                normal_queue.popleft()
            else:
                break

            room_queues_length[room_idx] -= 1

            # visiting_srv_end = visiting_patients[room_idx][min_doctor_idx][get_col_idx('srv_end')]
            visiting_srv_end = visiting_patients[room_idx][min_doctor_idx][5]
            if min_visit_end and min_visit_end > visiting_srv_end:
                visit_start = min_visit_end
            else:
                visit_start = visiting_srv_end

            # visiting_patients[room_idx][min_doctor_idx][get_col_idx('visit_beg')] = visit_start
            # visiting_patients[room_idx][min_doctor_idx][get_col_idx('room')] = room_idx
            # visiting_patients[room_idx][min_doctor_idx][get_col_idx('doctor')] = min_doctor_idx
            # visit_time = rgs.visit_time(Conf.DOCTORS[room_idx][min_doctor_idx])
            # visiting_patients[room_idx][min_doctor_idx][get_col_idx('visit_t')] = visit_time
            # visiting_patients[room_idx][min_doctor_idx][get_col_idx('visit_end')] = visit_start + visit_time
            visiting_patients[room_idx][min_doctor_idx][7] = visit_start
            visiting_patients[room_idx][min_doctor_idx][10] = room_idx
            visiting_patients[room_idx][min_doctor_idx][11] = min_doctor_idx
            visit_time = rgs.visit_time(Conf.DOCTORS[room_idx][min_doctor_idx])
            visiting_patients[room_idx][min_doctor_idx][8] = visit_time
            visiting_patients[room_idx][min_doctor_idx][9] = visit_start + visit_time

        if min_room_length > room_queues_length[room_idx]:
            min_room_length = room_queues_length[room_idx]
            min_room_length_idx = room_idx

    return min_room_length_idx


def add_to_room_queue(np_normal_table, np_corona_table, p_index, p_has_corona, visit_queues, room_queues_length,
                      arrive_time, visiting_patients):
    min_room_length_idx = flush_patients(visit_queues,
                                         room_queues_length,
                                         visiting_patients, arrive_time)
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


def run():

    # initialization
    init_pd()
    raw = raw_table()
    corona_table = raw.loc[raw['corona']].reset_index(drop=True)
    normal_table = raw.loc[~ raw['corona']].reset_index(drop=True)
    visiting_patients = [[None] * len(Conf.DOCTORS[i]) for i in range(len(Conf.DOCTORS))]
    visit_queues = [[deque(), deque()] for i in range(len(Conf.DOCTORS))]
    room_queues_length = [0 for i in range(len(Conf.DOCTORS))]

    # stats arrays
    rooms_length_over_time = np.array([[0 for x in range(Conf.CLIENT_NO)] for y in range(len(Conf.DOCTORS))])
    # response_time = [0 for i in range(len(Conf.CLIENT_NO))]

    # 0: normal,  1: corona plus
    patient_type_over_time = [[0 for x in range(Conf.CLIENT_NO)] for y in range(2)]



    insystem_realtime = [[0 for x in range(Conf.CLIENT_NO)] for y in range(2)]


    del raw
    j_max = Conf.CLIENT_NO // 100

    now = 0
    corona_idx = 0
    normal_idx = 0
    corona_len = len(corona_table)
    normal_len = len(normal_table)

    np_corona_table = corona_table.to_numpy()
    np_normal_table = normal_table.to_numpy()
    corona_as_t_idx = [corona_table.columns.get_loc(c) for c in ['arrival_t', 'srv_t', 'remaining_P']]
    corona_set_idx = [corona_table.columns.get_loc(c) for c in ['srv beg', 'srv_end', 'remaining_P']]
    normal_set_idx = [normal_table.columns.get_loc(c) for c in ['srv beg', 'srv_end', 'remaining_P']]
    normal_as_t_idx = [normal_table.columns.get_loc(c) for c in ['arrival_t', 'srv_t', 'remaining_P']]

    del corona_table
    del normal_table

    corona_arrival, corona_srv_t, c_Q_t = np_corona_table[corona_idx, corona_as_t_idx]
    normal_arrival, normal_srv_t, n_Q_t = np_normal_table[normal_idx, normal_as_t_idx]
    queue_arr = np.array([-1] * Conf.CLIENT_NO)
    _srv_beg_cache = np.array([])
    for i in range(100):
        print("#" * i + "-" * (99 - i), end="\r")
        for j in range(j_max):
            patient_index = i * j_max + j
            gone = False
            if corona_idx != corona_len and (
                    corona_arrival <= now or corona_arrival <= normal_arrival or normal_idx == normal_len):
                p_index = corona_idx
                p_has_corona = True
                arrival_t = corona_arrival
                begin = now if corona_arrival < now else corona_arrival
                c_Q_t -= (begin - corona_arrival)
                if c_Q_t >= 0:
                    now = end = corona_srv_t + begin
                    np_corona_table[corona_idx, corona_set_idx] = begin, end, c_Q_t
                else:
                    np_corona_table[corona_idx, 6] = "gone"
                    np_corona_table[corona_idx, 5] = "gone"
                    gone = True

                corona_idx += 1
                if corona_idx != corona_len:
                    corona_arrival, corona_srv_t, c_Q_t = np_corona_table[corona_idx, corona_as_t_idx]
            else:
                p_index = normal_idx
                arrival_t = normal_arrival
                p_has_corona = False
                begin = now if normal_arrival < now else normal_arrival
                n_Q_t -= (begin - normal_arrival)
                if n_Q_t >= 0:
                    now = end = normal_srv_t + begin
                    np_normal_table[normal_idx, normal_set_idx] = begin, end, n_Q_t
                else:
                    np_normal_table[normal_idx, 6] = "gone"
                    np_normal_table[normal_idx, 5] = "gone"
                    gone = True
                normal_idx += 1
                if normal_idx != normal_len:
                    normal_arrival, normal_srv_t, n_Q_t = np_normal_table[normal_idx, normal_as_t_idx]

            patient_type_over_time[0][patient_index] = normal_idx
            patient_type_over_time[1][patient_index] = corona_idx
            ix = 0
            _srv_beg_cache = np.append(_srv_beg_cache, begin)
            for e in _srv_beg_cache:
                if e > arrival_t:
                    break
                else:
                    ix += 1
            _srv_beg_cache = _srv_beg_cache[ix:]
            queue_arr[corona_idx + normal_idx - 1] = _srv_beg_cache.shape[0]

            # saving room queue length for stats
            if patient_index != 0:
                for k in range(len(room_queues_length)):
                    rooms_length_over_time[k][patient_index] = room_queues_length[k]
                    if k == 0:
                        rooms_length_over_time[k][patient_index] -= 1
            tmp_sum = 0
            for y in range(len(Conf.DOCTORS)):
                tmp_sum += rooms_length_over_time[y][patient_index]
            insystem_realtime[1][patient_index] = (tmp_sum + queue_arr[patient_index])//9
            insystem_realtime[0][patient_index] = tmp_sum + queue_arr[patient_index] - insystem_realtime[1][patient_index]
            if gone is False:
                add_to_room_queue(np_normal_table, np_corona_table, p_index, p_has_corona, visit_queues,
                                  room_queues_length,
                                  now, visiting_patients)


    print()
    flush_patients(visit_queues, room_queues_length,
                   visiting_patients)

    corona_table = pd.DataFrame(np_corona_table, columns=Conf.TABLE_COLUMNS)
    normal_table = pd.DataFrame(np_normal_table, columns=Conf.TABLE_COLUMNS)
    complete_table = normal_table.append(corona_table, ignore_index=True)

    del normal_table, corona_table
    complete_table = complete_table.sort_values(by=['arrival_t'], ignore_index=True)
    complete_table['queue_length'] = queue_arr

    # =========================================== getting statistics ============================================

    not_gone_table = complete_table[complete_table.remaining_P != 'gone']
    gone_table = complete_table[complete_table.remaining_P == 'gone']

    # 1,2- in system time and in queue time
    mean_corona_insystem_time = (gone_table[gone_table.corona == True]['init_patience'].sum() +
                                 not_gone_table[not_gone_table.corona == True]['visit_end'].sum() -
                                 not_gone_table[not_gone_table.corona == True]['arrival_t'].sum() +
                                 gone_table[gone_table.srv_end != 'gone'][gone_table.corona == True][
                                     'srv_t'].sum()) / (len(complete_table[complete_table.corona == True]))

    mean_normal_insystem_time = (gone_table[gone_table.corona != True]['init_patience'].sum()
                                 + not_gone_table[not_gone_table.corona != True]['visit_end'].sum() -
                                 not_gone_table[not_gone_table.corona != True]['arrival_t'].sum() +
                                 (gone_table[gone_table.srv_end != 'gone'][gone_table.corona != True][
                                      'srv_t'].sum())) / (len(complete_table[complete_table.corona != True]))

    mean_corona_inqueue_time = (gone_table[gone_table.corona == True]['init_patience'].sum() +
                                not_gone_table[not_gone_table.corona == True]['visit_end'].sum() -
                                not_gone_table[not_gone_table.corona == True]['arrival_t'].sum() -
                                not_gone_table[not_gone_table.corona == True]['srv_t'].sum() -
                                not_gone_table[not_gone_table.corona == True]['visit_t'].sum()) / (
                                   len(complete_table[complete_table.corona == True]))

    mean_normal_inqueue_time = (gone_table[gone_table.corona != True]['init_patience'].sum() +
                                not_gone_table[not_gone_table.corona != True]['visit_end'].sum() -
                                not_gone_table[not_gone_table.corona != True]['arrival_t'].sum() -
                                not_gone_table[not_gone_table.corona != True]['srv_t'].sum() -
                                not_gone_table[not_gone_table.corona != True]['visit_t'].sum()) / (
                                   len(complete_table[complete_table.corona != True]))

    overal_insystem_time = (len(complete_table[complete_table.corona == True]) * mean_corona_insystem_time + \
                            len(complete_table[complete_table.corona != True]) * mean_normal_insystem_time) / \
                           (len(complete_table))

    overal_inqueue_time = (len(complete_table[complete_table.corona == True]) * mean_corona_inqueue_time + \
                           len(complete_table[complete_table.corona != True]) * mean_normal_inqueue_time) / \
                          (len(complete_table))

    print('*********************************************** statistics ***********************************************')
    print('========================== mean in_system time ============================')
    print("mean_normal_insystem_time:", end=' ')
    print("%.3f"%mean_normal_insystem_time)
    print("mean_corona_insystem_time:", end=' ')
    print("%.3f"% mean_corona_insystem_time)
    print("overal_insystem_time:", end=' ')
    print("%.3f"%overal_insystem_time)

    print('========================== mean in_queue time ============================')
    print("mean_normal_inqueue_time:", end=' ')
    print("%.3f"%mean_normal_inqueue_time)
    print("mean_corona_inqueue_time:", end=' ')
    print("%.3f"%mean_corona_inqueue_time)
    print("overal_inqueue_time:", end=' ')
    print("%.3f"%overal_inqueue_time)

    print('========================== 3 ============================')
    # 3-number of gone people
    gone_count = len(gone_table)
    print('number of gone patients during simulation:', end=' ')
    print(gone_count)


    print('========================== mean visit and rooms queue length ============================')
    # 4- mean service and visit queue length
    mean_service_queue_length = complete_table['queue_length'].mean()
    print('mean_service_queue_length:', end=' ')
    print("%.3f"%mean_service_queue_length)

    mean_visit_queue_length = [0 for x in range(len(Conf.DOCTORS))]

    print('mean_rooms_queue_length:')
    for i in range(len(Conf.DOCTORS)):
        print('room number {}:'.format(i), end=' ')
        mean_visit_queue_length[i] = rooms_length_over_time[i][:].mean()
        print("%.3f"%mean_visit_queue_length[i])


    # # 5- accuracy
    print("===== accuracy =======")
    acur = complete_table['srv_t'].values

    acc_return_val = 1.96*acur.std()/(np.sqrt(Conf.CLIENT_NO)*acur.mean())
    print("accuracy with {} number of patients".format(Conf.CLIENT_NO))
    print("%.4f"%(1 - acc_return_val))

    #print(rooms_length_over_time)

    # emtiazi 1
    normal_response_table = complete_table[complete_table.corona == False][['srv_t', 'visit_t', 'arrival_t']]
    normal_response_table['response_time'] = normal_response_table['srv_t'] + normal_response_table['visit_t']
    normal_response_table['response_time'] = normal_response_table['response_time'].fillna(0)

    # print(normal_response_table)
    labels = normal_response_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, normal_response_table['response_time'])
    ax.set(xlabel='time', ylabel='normal patients response freq', title='normal patients response frequency')
    fig.savefig("plots/normal_response_plot.png")

    corona_response_table = complete_table[complete_table.corona == True][['srv_t', 'visit_t', 'arrival_t']]
    corona_response_table['response_time'] = corona_response_table['srv_t'] + corona_response_table['visit_t']
    corona_response_table['response_time'] = corona_response_table['response_time'].fillna(0)

    # print(len(normal_response_table))
    labels = corona_response_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, corona_response_table['response_time'])
    ax.set(xlabel='time', ylabel='corona+ patients response freq', title='corona+ patients response frequency')
    fig.savefig("plots/corona_response_plot.png")

    del normal_response_table, corona_response_table

    # emtiazi 2
    gone_table['waiting_time'] = gone_table['init_patience']
    not_gone_table['waiting_time'] = not_gone_table['visit_end'] - not_gone_table['srv_t'] - \
                                     not_gone_table['visit_t'] - not_gone_table['arrival_t']

    overal_waiting = gone_table.append(not_gone_table, ignore_index=True)
    overal_waiting = overal_waiting.sort_values(by=['arrival_t'], ignore_index=True)

    corona_waiting = overal_waiting[overal_waiting.corona == True][['waiting_time', 'arrival_t']]
    normal_waiting = overal_waiting[overal_waiting.corona == False][['waiting_time', 'arrival_t']]
    # print(overal_waiting)

    labels = corona_waiting['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, corona_waiting['waiting_time'])
    ax.set(xlabel='time', ylabel='corona+ patients waiting time', title='corona+ patients waiting frequency')
    fig.savefig("plots/corona_waiting_freq.png")

    labels = normal_waiting['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, normal_waiting['waiting_time'])
    ax.set(xlabel='time', ylabel='normal patients waiting time', title='normal patients waiting frequency')
    fig.savefig("plots/normal_waiting_freq.png")

    del corona_waiting, normal_waiting,
    # emtiazi 3

    labels = complete_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, insystem_realtime[0])
    ax.set(xlabel='time', ylabel='normal in patient system freq', title='normal patients in system frequency')
    fig.savefig("plots/normal_insystem_freq.png")

    labels = complete_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, insystem_realtime[1])
    ax.set(xlabel='time', ylabel='corona in patient system freq', title='corona patients in system frequency')
    fig.savefig("plots/corona_insystem_freq.png")


    #print(insystem_realtime[1])

    # emtiazi 4
    labels = complete_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, patient_type_over_time[0][:])
    ax.set(xlabel='time', ylabel='normal patients number in system(accumulated)',
           title='normal patients number in system(accumulated)')
    fig.savefig("plots/normal_accumulated_insystem.png")

    labels = complete_table['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, patient_type_over_time[1][:])
    ax.set(xlabel='time', ylabel='corona patients number in system(accumulated)',
           title='corona patients number in system(accumulated)')
    fig.savefig("plots/corona_accumulated_insystem.png")

    labels = complete_table['arrival_t']
    fig, ax = plt.subplots()
    overal_over_time = [patient_type_over_time[0][i] + patient_type_over_time[1][i] for i in range(len(patient_type_over_time[0]))]
    ax.plot(labels, overal_over_time)
    ax.set(xlabel='time', ylabel='overal patients number in system(accumulated)',
           title='overal patients number in system(accumulated)')
    fig.savefig("plots/overal_accumulated_insystem.png")


    #print(patient_type_over_time[0])


    # emtiazi 5
    normal_queue_length = complete_table[complete_table.corona == False][['queue_length', 'arrival_t']]
    labels = normal_queue_length['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, normal_queue_length['queue_length'])
    ax.set(xlabel='time', ylabel='normal service queue length', title='normal service queue length plot')
    fig.savefig("plots/normal_service_queue_length.png")

    corona_queue_length = complete_table[complete_table.corona == True][['queue_length', 'arrival_t']]
    labels = corona_queue_length['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, corona_queue_length['queue_length'])
    ax.set(xlabel='time', ylabel='corona service queue length', title='corona service queue length plot')
    fig.savefig("plots/corona_service_queue_length.png")

    overal_queue_length = complete_table[['queue_length', 'arrival_t']]
    labels = overal_queue_length['arrival_t']
    fig, ax = plt.subplots()
    ax.plot(labels, overal_queue_length['queue_length'])
    ax.set(xlabel='time', ylabel='overal service queue length', title='overal service queue length plot')
    fig.savefig("plots/overal_service_queue_length.png")


    return rooms_length_over_time, acc_return_val


if __name__ == '__main__':
    init_conf()
    run()