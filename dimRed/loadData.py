#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Supports loading different data sets.
"""

import csv
import numpy as np
import os

from dimRed import highDimData
from dimRed import settingsIO

"""
Load file containing dataset paths.
"""
def getDatasetPaths(path):
    # load file and save in directory for ids
    paths = []
    with open(path, 'rt') as inFile:
        lines = inFile.readlines()

        for line in lines:
            line = line.split("#", 1)[0]
            line = line.strip()
            if len(line) > 0:
                paths.append(line)

    return paths

"""
Loads an overview of all available trials with their paths and types. (Step 1)
"""
def getAllTrials(path):
    # load file and save in directory for ids
    data = {}
    with open(path, 'rt') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # ignore rows starting with # or not 3 columns
        for row in fileReader:
            if len(row) == 3:
                if row[0][0] != "#":
                    row[1] = row[1].strip()
                    if row[1].startswith("["):
                        paths = row[1][1:-1]
                        paths = paths.replace("\\", "/")
                        paths = paths.split(";")
                        paths = [p.replace("/", os.sep) for p in paths]

                    else:  # just one path given
                        paths = row[1].replace("/", os.sep).replace("\\", os.sep).replace(";", ",")
                        paths = [paths]
                    data[row[0]] = (paths, row[2].strip())

    return data

"""
Loads an overview of all available trials with their paths and types. (Step 2)
"""
def getAllPreprocessedTrials(path):
    # load file and save in directory for ids
    data = {}
    with open(path, 'rt') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # ignore rows starting with # or not 3 columns
        for row in fileReader:
            if len(row) == 5:
                if row[0][0] != "#":
                    data[row[0]] = [row[1].strip().replace("/", os.sep).replace("\\", os.sep),  # path
                                    row[2].strip().replace("/", os.sep).replace("\\", os.sep),  # settings
                                    row[3].strip(),  # orig data file(s)
                                    row[4].strip()]  # orig data type

    return data

"""
Loads an overview of all available trials with their paths and types. (Step 3)
"""
def getAllVisTrials(path):
    # load file and save in directory for ids
    data = {}
    with open(path, 'rt') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # ignore rows starting with # or not 3 columns
        for row in fileReader:
            if len(row) >= 4:
                if row[0][0] != "#":
                    data[row[0]] = {}
                    data[row[0]]["2DData_path"] = row[1].strip().replace("/", os.sep).replace("\\", os.sep)
                    data[row[0]]["settings_path"] = row[2].strip().replace("/", os.sep).replace("\\", os.sep)
                    data[row[0]]["preprocessSettings_path"] = row[3].strip().replace("/", os.sep).replace("\\", os.sep)
                    data[row[0]]["highDimData_path"] = row[4].strip().replace("/", os.sep).replace("\\", os.sep)
                    data[row[0]]["highDimData_type"] = row[5].strip()
                    data[row[0]]["preprocessedData_path"] = row[6].strip().replace("/", os.sep).replace("\\", os.sep)
    return data

"""
Loads a data set with the given id, path and type.
"""
def getPreprocessedDataForVis(dataPath, settingsPath, preprocessingSettingsPath, cS):
    dataPoints = []
    settings, preprocessingSettings = {}, {}

    if settingsPath and os.path.isfile(settingsPath):
        settings = settingsIO.getSettings(settingsPath)

        settingsIO.changeSettings(settings, cS)

    if preprocessingSettingsPath and os.path.isfile(preprocessingSettingsPath):
        preprocessingSettings = settingsIO.getSettings(preprocessingSettingsPath)

    dataPointsList = []
    X_embedded = []
    if dataPath and os.path.isfile(dataPath):
        with open(dataPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')

            for i, row in enumerate(reader):
                if not row:
                    if dataPoints:
                        dataPointsList.append(dataPoints)
                        dataPoints = []
                else:
                    # first two columns: x and y values
                    dataPoints.append([float(row[0]), float(row[1]), row[2].lower() == "true",
                                       row[3] if row[2].lower() == "true" else ""])  # x, y, mainSample, label
                    X_embedded.append(np.asarray([float(row[0]), float(row[1])]))
            if dataPoints:
                dataPointsList.append(dataPoints)

    return dataPointsList, settings, preprocessingSettings, X_embedded

"""
Loads a data set from the given path.
"""
def getPreprocessedDataForDimRed(dataPath, cS):
    print("Loading data...")
    print(dataPath)
    m = []
    labels = []
    if dataPath and os.path.isfile(dataPath):
        m, labels = highDimData.getDataForCSVFile(dataPath, cS)  # returns lists

    # add time series id to label if there is more than one time series
    if len(m) > 1:
        for i in range(len(labels)):
            for j in range(len(labels[i])):
                labels[i][j] = "T-{} {}".format(i, labels[i][j])

    return m, labels

"""
Loads one (or multiple) data set(s) with the given id, path and type.
"""
def getTrialData(trial, paths, t, cS):

    labels = []
    m = []
    width = 0
    height = 0
    dataLengths = [0]  # just needed if multiple datasets are loaded (not supported for all datasets)

    print("Load trial: {} - {} - {} ...".format(trial, paths, t))

    # many csv files (TODO supports just one data set)
    if t == "csv_multipleFiles":
        print("Many CSV files")

        m, labels = highDimData.getDataForManyCSVFiles(paths)

    # xml files (repos) (TODO supports just one data set)
    elif t == "bgraph":
        print("BGRAPH")
        m, labels = highDimData.getDataForBgraph(paths)

    # videos (TODO supports just one data set)
    elif t == "images":
        print("VIDEO")

        files = []

        imgIndex = -1
        path = paths[0]  # first path
        for file in os.listdir(path):
            imgIndex += 1
            if file.endswith(".JPG") or file.endswith(".jpg") and imgIndex % cS.everyXSample == 0:
                files.append(os.path.join(path, file))
        files.sort()

        m, labels, width, height = highDimData.getDataFromImages(files)

    # common csv file (multiple data sets possible)
    elif t == "csv":
        print("CSV")

        m, labels, dataLengths = highDimData.getDataForCSVFiles(paths, cS)

    else:
        print("ERROR")
        print(t)

    print("...trial loaded")

    return m, dataLengths, labels, width, height
