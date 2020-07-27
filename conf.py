import argparse


def get_conf_terminal():
    first_line = input()
    lines = first_line + '\n'
    big_m = int(float(first_line.replace(' ', '').split(',')[0]))
    print(big_m)
    for m in range(big_m):
        lines += input() + '\n'
    return lines


def parse_conf(s):
    s_split = s.split('\n')
    s_split = s_split[:s_split.index("")]
    first_line = s_split.pop(0)
    return_list = list(map(float, first_line.replace(' ', '').split(',')))
    return_list.append([list(map(float, r.replace(' ', '').split(','))) for r in s_split])
    return return_list


def init_conf(conf_file=None):
    if conf_file is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', '-c', help="path to config file")
        conf_file = parser.parse_args().config

    conf_str = open(conf_file).read() if conf_file else get_conf_terminal()
    Conf.M, Conf.LAMBDA, Conf.ALPHA, Conf.MU, Conf.DOCTORS = parse_conf(conf_str)
    Conf.M = int(Conf.M)


class Conf:
    CLIENT_NO = 100000
    TABLE_COLUMNS = ["t btw arrival", "arrival_t", "corona", "srv beg", "srv_t", "srv_end", "remaining_P", "visit_beg",
                     "visit_t", "visit_end", "room", "doctor", "init_patience"]

    M, LAMBDA, ALPHA, MU, DOCTORS = None, None, None, None, None
