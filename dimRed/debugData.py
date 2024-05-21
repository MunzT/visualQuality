#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
For debugging / saving plots.
"""

from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import os
matplotlib.use('Agg')

from dimRed import settingsIO
from dimRed.settings import pathSettings

debugPrints = False
debugPlots = False  # activate for detailed plots (when using the visualization tool)
savePlots = True  # only used if also debugPlots is true
showPlots = False

cS = None
selectedDataset = ""

def setDataSet(_selectedDataset, _cS):
    global cS
    global selectedDataset
    cS = _cS
    selectedDataset = _selectedDataset

def debugData(data, dataName):
    global selectedDataset
    debugDataSimple(data, dataName, False)
    plotHistogram(data, dataName, dataName, dataName)

    if debugPrints:
        print("****************************************************************************************************")
        print("****************************************************************************************************")

def debugDataSimple(data, dataName, printSeparator=True):

    if not debugPrints:
        return

    print("---", dataName, "---")
    print(type(data))
    if type(data) == list:
        print("len list :", len(data))
        if data:
            print("sub type", type(data[0]))
            if type(data[0]) == list:
                print("len sublist :", len(data[0]))
            if type(data[0]) == np.ndarray:
                print("sub shape :", data[0].shape)

    if type(data) == np.ndarray:
        print("shape: ", data.shape)
        if data.size > 0:
            print("sub type", type(data[0]))
            if type(data[0]) == list:
                print("len sublist :", len(data[0]))
            if type(data[0]) == np.ndarray:
                print("sub shape :", data[0].shape)
    print(data)

    if printSeparator:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

def plotHistogram(data, yLabel, title, fileDescription):
    if not debugPlots:
        return

    # rearrange Data
    newData = []
    if type(data) == list:
        for i in range(len(data)):
            for j in range(len(data[i])):
                newData.append(data[i][j])
    elif type(data) == np.ndarray:
        for i in range(data.shape[0]):
            for j in range(data[i].shape[0]):
                newData.append(data[i][j])
    newData = np.asarray(newData)

    y_pos = np.arange(len(newData))

    data_labels = [i for i, _ in enumerate(newData)]

    plt.bar(y_pos, newData, align='center', alpha=0.5, color=['red' if el > 0 else 'blue' for el in newData])
    plt.xticks(y_pos, data_labels)
    plt.xlabel('Time')
    plt.ylabel(yLabel)
    plt.title(title)

    # save image
    if savePlots:
        now = datetime.now()
        dateTime = now.strftime("%Y-%d-%m-%H-%M-%S")

        dirName = settingsIO.settingsDirName(cS, selectedDataset)
        path = os.path.join(*[pathSettings.statDir, selectedDataset, "{}_{}_{}.png".format(dirName, fileDescription, dateTime)])

        print("PATH:" + path)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        figure = plt.gcf()
        figure.set_size_inches(20, 20)
        plt.savefig(path)
        plt.close("all")

    if showPlots:
        plt.show()

def plotScatterplot(xValues, yValues, xLabel, yLabel, title, fileDescription, connected=False, maxX=0, maxY=0):

    if not debugPlots:
        return

    alpha = 0.1

    plt.plot(xValues, yValues, 'bo', alpha=alpha, markersize=3, markevery=10)

    if connected:
        plt.plot(xValues, yValues, color="black", alpha=0.01)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)

    if maxX > 0 and maxY > 0:
        plt.axis([0, maxX, 0, maxY])

    # save image
    if savePlots:
        now = datetime.now()
        dateTime = now.strftime("%Y-%d-%m-%H-%M-%S")

        dirName = settingsIO.settingsDirName(cS, selectedDataset)
        path = os.path.join(*[pathSettings.statDir, selectedDataset, "{}_{}_{}.png".format(dirName, fileDescription, dateTime)])

        print("PATH:" + path)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        figure = plt.gcf()
        figure.set_size_inches(20, 20)
        plt.savefig(path)
        plt.close("all")

    if showPlots:
        plt.show()
