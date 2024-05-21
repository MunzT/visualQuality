import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import csv
import math
from scipy.special import gamma
import random
from mpl_toolkits.mplot3d import Axes3D

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
    ax.scatter3D(x, y, z, c=t, cmap='Greens');
    plt.savefig(fileName + "_.png")
    plt.close()

    # write to file
    with open(fileName + ".csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(zip(x, y, z))
        
    
######## Spiral ########
x = []
y = []
z = []
for t in np.arange(0.0, 6 * math.pi, math.pi / 100 * 6):
    x.append(t * math.cos(t))
    y.append(t * math.sin(t))
    z.append(t)

save(x, y, z, 'spiral')




