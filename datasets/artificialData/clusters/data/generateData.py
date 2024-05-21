import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import csv
import random

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

    sections = [10, 40, 60, 100]
    currentId = 0

    x = []
    y = []
    z = []

    for i in range(n):

        if currentId % 4 == 0:
            x.append(0 + random.random()*0.5)
            y.append(0 + random.random()*0.5)
            z.append(0 + random.random()*0.5)
        elif currentId % 4 == 1:
            x.append(10 + random.random()*0.5)
            y.append(0 + random.random()*0.5)
            z.append(0 + random.random()*0.5)
        elif currentId % 4 == 2:
            x.append(5 + random.random()*0.5)
            y.append(5 + random.random()*0.5)
            z.append(0 + random.random()*0.5)
        elif currentId % 4 == 3:
            x.append(5 + random.random()*0.5)
            y.append(-5 + random.random()*0.5)
            z.append(0 + random.random()*0.5)

        if i > sections[currentId]:
            currentId += 1

    save(x, y, z, 'clusters')
