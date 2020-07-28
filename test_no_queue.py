import simulator
from conf import init_conf
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # check for 2 rooms that each has 2 doctors
    visit_rate = [1, 1, 1, 1]
    content = None
    plot_array = []

    while(True):
        content = "2, 6, 20, 5\n{}, {}\n{}, {}\n".format(visit_rate[0], visit_rate[1], visit_rate[2], visit_rate[3])
        file = open("conf", "w")
        file.write(content)
        file.close()
        init_conf('conf')
        r, _ = simulator.run()
        plot_array.append(sum(r[0]) + sum(r[1]))
        if (sum(r[0]) + sum(r[1])) == 0:
            break
        else:
            for i in range(len(visit_rate)):
                visit_rate[i] += 1
    print("ideal doctors visit rate:")
    print(visit_rate)

    labels = range(len(plot_array))
    fig, ax = plt.subplots()
    ax.plot(labels, plot_array)
    ax.set(xlabel="doctors service rate", ylabel='number of patients in rooms  queue', title='Check if queues are empty in rooms')
    fig.savefig("plots/test_no_queue.png")

