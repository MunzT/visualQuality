import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import csv

def save(x, y, z, fileName):

    t = np.arange(len(x))

    # plot
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    fig.set_size_inches(20, 20, 20)

    ax.plot3D(x, y, z, "blue")
    plt.savefig(fileName + ".png")
    plt.close()

    ax = plt.axes(projection='3d')
    fig.set_size_inches(20, 20, 20)
    ax.scatter3D(x, y, z, c=t, cmap='Greens')
    plt.savefig(fileName + "_.png")
    plt.close()

    # write to file
    with open(fileName + ".csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(zip(x, y, z))

numSamples = [100]

for n in numSamples:
    x = []
    y = []
    z = []
    for i in range(n):
        x.append(i/n)
        y.append(1/2)
        z.append(1/2)

    save(x, y, z, 'line_1_{}'.format(n))

    x = []
    y = []
    z = []
    for i in range(n):
        x.append(1/2)
        y.append(i/n)
        z.append(1/2)

    save(x, y, z, 'line_2_{}'.format(n))
