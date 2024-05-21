#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Creates static visualization and saves them to files: circles, lines and labels.
"""

from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os

from dimRed import interpolate
from dimRed import settingsIO
from dimRed.settings import pathSettings
from dimRed import myTypes

"""
Creates the plot: Main circles, sub circles, and lines.
"""
def plotFigure(X_embeddedLists, mainSamplesList, labelsList, cS, newName, save=True, showLabels=False):
    print("Plot figure...")

    # draw points with curves or lines
    plt.figure(figsize=(12, 10))
    ax = plt.subplot(111)
    ax.set_aspect('equal', 'datalim')

    startColors = [[1, 0, 1], [1, 1, 0], [1, 0, 0]]
    endColors = [[0, 0, 1], [0, 1, 0], [0, 1, 1]]

    for i in range(len(mainSamplesList)):
        mainSamples = mainSamplesList[i]
        labels = labelsList[i]
        X_embedded = X_embeddedLists[i]

        if cS.subsampleType == myTypes.SampleInterpolation.line:
            drawWithLines(X_embedded, mainSamples, ax, startColors[i % len(startColors)], endColors[i % len(endColors)])
        elif cS.subsampleType == myTypes.SampleInterpolation.catmullRom or \
                cS.subsampleType == myTypes.SampleInterpolation.centripetalCatmullRom:
            drawWithCatmullRom(X_embedded, mainSamples, ax, cS.subsampleType, startColors[i % len(startColors)],
                               endColors[i % len(endColors)])

        # highlight first and last point
        ax.scatter(X_embedded[0][0], X_embedded[0][1], alpha=1, facecolors='none',
                   edgecolors=startColors[i % len(startColors)], s=200, zorder=3)
        ax.scatter(X_embedded[-1][0], X_embedded[-1][1], alpha=1, facecolors='none',
                   edgecolors=endColors[i % len(endColors)], s=200, zorder=3)

        # labels
        if showLabels:
            annotations = []
            if labels == [] or cS.continuousLabels:
                labels = ['{0}'.format(i + 1) for i in range(len(X_embedded))]
            else:
                newLabels = []
                count = 0
                for j in range(len(X_embedded)):
                    if not cS.subsampleInHighDimSpace:
                        newLabels.append(labels[j])
                    elif mainSamples[j]:
                        newLabels.append(labels[count])
                        count += 1
                    else:
                        newLabels.append("")
                labels = newLabels

            for label, x, y in zip(labels, X_embedded[:, 0], X_embedded[:, 1]):
                if label != "":
                    ann = ax.annotate(
                        label,
                        xy=(x, y), xytext=(-10, 10),
                        textcoords='offset points', ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.1', fc='blue', alpha=0.2),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                    ann.set_visible(True)
                    annotations.append(ann)

    # save image
    if save:
        now = datetime.now()
        dateTime = now.strftime("%Y-%d-%m-%H-%M-%S")

        dirName = settingsIO.settingsDirName(cS, newName)
        subdir = "-".join(newName.split("-")[:-1])
        path = os.path.join(*[pathSettings.imageDir, subdir, "{}_{}.png".format(dirName, dateTime)])

        print("PATH:" + path)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path, bbox_inches='tight')
        plt.close("all")

    if False:
        plt.show()

    print("...plot finished")

"""
Creates straight lines for the plot.
"""
def drawWithLines(values, mainSamples, ax, startColor, endColor):
    print("...with lines...")

    ax.plot(values[:, 0], values[:, 1], zorder=1, lw=1, alpha=.5, color=(.5, .5, .5, 1))

    colors = [[(endColor[0] - startColor[0]) * i / len(values) + startColor[0],
               (endColor[1] - startColor[1]) * i / len(values) + startColor[1],
               (endColor[2] - startColor[2]) * i / len(values) + startColor[2]]
              for i in range(len(values))]
    scatter = []
    count = 0
    for data, mainSample, color in zip(values, mainSamples, colors):
        x, y = data
        if mainSample:
            size = 25
        else:
            size = 2
        scatter.append(ax.scatter(x, y, c=[color], zorder=2, picker=5, s=size))
        count += 1

    print("...drawing Lines finished")

"""
Creates catmull rom curves for the plot.
"""
def drawWithCatmullRom(values, mainSamples, ax, lines, startColor, endColor):
    # Calculate the Catmull-Rom splines through the points
    print("...with curves ({})...".format(lines))

    samples = []
    if lines == myTypes.SampleInterpolation.catmullRom:
        samples = interpolate.CatmullRomChain(values)
    elif lines == myTypes.SampleInterpolation.centripetalCatmullRom:
        samples = interpolate.CentripetalCatmullRomChain(values)

    samples = [x for i in range(len(samples)) for x in samples[i]]

    # Convert the Catmull-Rom curve points into x and y arrays and plot
    x, y = zip(*samples)
    ax.plot(x, y, lw=1, alpha=.5, zorder=1, color=(.5, .5, .5, 1))

    colors = [[(endColor[0] - startColor[0]) * i / len(values) + startColor[0],
               (endColor[1] - startColor[1]) * i / len(values) + startColor[1],
               (endColor[2] - startColor[2]) * i / len(values) + startColor[2]]
              for i in range(len(values))]
    scatter = []
    count = 0
    for data, mainSample, color in zip(values, mainSamples, colors):
        x, y = data
        if mainSample:
            size = 25
        else:
            size = 2
        scatter.append(ax.scatter(x, y, c=[color], zorder=2, picker=5, s=size))
        count += 1

    print("...drawing Catmull Rom finished...")
