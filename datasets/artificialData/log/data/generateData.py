import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import csv
import math

def save(x, y, fileName):
    # plot
    fig = plt.figure()
    fig.set_size_inches(20, 20)
    ax = fig.add_subplot(111)

    plt.plot(x, y)
    plt.savefig(fileName + ".png")
    plt.close()

    fig = plt.figure()
    fig.set_size_inches(20, 20)
    ax = fig.add_subplot(111)

    plt.scatter(x, y, s=4)
    plt.savefig(fileName + "_.png")
    plt.close()

    # write to file
    with open(fileName + ".csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(zip(x, y))

# log(x)
x = [i / 100 for i in range(1, 1000)]
y = [math.log2(i) for i in x]
x = [0 for i in range(1, 1000)]

save(x, y, 'log_time')
