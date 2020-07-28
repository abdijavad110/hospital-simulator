import simulator
from conf import init_conf, Conf
if __name__ == '__main__':

    for i in range(1000, 2000, 50):
        Conf.CLIENT_NO = i
        init_conf('conf')
        _, accuracy = simulator.run()
        if accuracy < 0.05:
            result = "sufficient number of patients for 95% accuracy: {}".format(i)
            file = open('accuracy_result.txt', 'w')
            file.write(result)
            file.close()
            break