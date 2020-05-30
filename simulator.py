import argparse


def get_conf_terminal():
    first_line = input()
    lines = first_line + '\n'
    big_m = int(float(first_line.replace(' ', '').split(',')[0]))
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help="path to config file")
    conf_file = parser.parse_args().config

    conf_str = open(conf_file).read() if conf_file else get_conf_terminal()
    M, lamb, alpha, mu, doctors = parse_conf(conf_str)
    M = int(M)

    # initiate and start simulation
