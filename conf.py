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


def init_conf():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help="path to config file")
    conf_file = parser.parse_args().config

    conf_str = open(conf_file).read() if conf_file else get_conf_terminal()
    return parse_conf(conf_str)


class Conf:
    CLIENT_NO = 10
    TABLE_COLUMNS = ["t btw arrival", "arrival t", "corona +", "srv beg", "srv t", "srv end", "remaining P", "visit beg",
                     "visit t", "visit end", "room", "doctor", "init patience"]

    M, LAMBDA, ALPHA, MU, DOCTORS = init_conf()
    M = int(M)
