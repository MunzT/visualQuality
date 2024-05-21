#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Saves the coordinates of the embedding in a text file.
"""

from datetime import datetime
from shutil import copyfile
import os
import pathlib

from . import settingsIO
from .settings import pathSettings

"""
Saves all coordinates of the 2D embedding, if coordinates belong to a main sample and labels.
"""
def saveCoordinatesOfEmbedding(X_embeddedList, mainSamplesList, labelsList, cS, preprocessingSettings, newName):
    print("Save file with samples")

    subdir = "-".join(newName.split("-")[:-1])
    now = datetime.now()
    dateTime = now.strftime("%Y-%d-%m-%H-%M-%S")

    # save coordinates to file
    dirName = settingsIO.settingsDirName(cS, newName)
    path = os.path.join(*[pathSettings.visDataDir, subdir, dirName])

    if not os.path.exists(path):
        os.makedirs(path)

    dataPath = os.path.join(path, "data_{}_{}.points".format(newName, dateTime))
    with open(dataPath, "w") as f:
        for current_id in range(len(X_embeddedList)):
            X_embedded = X_embeddedList[current_id]
            mainSamples = mainSamplesList[current_id]
            labels = labelsList[current_id]
            c = 0

            for i, values in enumerate(X_embedded):
                f.write("{},{},{},{}\n".format(values[0], values[1], mainSamples[i], labels[c] if mainSamples[i] else ""))
                if mainSamples[i]:
                    c += 1

            f.write("\n")

    settingsPath = os.path.join(path, "data_{}_{}.toml".format(newName, dateTime))
    with open(settingsPath, "w") as f:
        f.write(settingsIO.settingsMetadata(cS))

    preprocessingSettingsPath = os.path.join(path, os.path.splitext(os.path.basename(preprocessingSettings))[0]
                                             + "_{}_.toml".format(dateTime))
    copyfile(preprocessingSettings, preprocessingSettingsPath)

    return dataPath, settingsPath, preprocessingSettingsPath

"""
Saves the given data as csv file.
"""
def saveData(data, dataLengths, path, fileAddition, cS, origDims):
    print("Save file:")

    now = datetime.now()
    dateTime = now.strftime("%Y-%d-%m-%H-%M-%S")

    if not os.path.exists(path):
        os.makedirs(path)

    saveFilePath = path + "/{}_{}_{}.csv".format(cS.trial, fileAddition, dateTime)
    settingsPath = path + "/{}_{}_{}.toml".format(cS.trial, fileAddition, dateTime)

    print("File name: " + saveFilePath)

    count = 0
    listId = 0
    nextEmptyLine = dataLengths[listId]
    with open(saveFilePath, "w") as f:
        for el in data:
            f.write("{}\n".format(",".join([str(x) for x in el])))
            count += 1
            if count == nextEmptyLine:
                f.write("\n")
                if len(dataLengths) > listId + 1:
                    listId += 1
                    nextEmptyLine = dataLengths[listId]
                    count = 0

    with open(settingsPath, "w") as f:
        f.write(settingsIO.settingsPreprocessing(cS, origDims))

    return saveFilePath, settingsPath

"""
Adds a new entry to the dataset list.
"""
def addToPreprocessedDataList(exportFile, current_id, filePath, settingsPath, origDataPaths, origDataType):

    if not os.path.exists(exportFile):
        # header
        with open(exportFile, 'w') as f:
            f.write('# orig id, path to csv file with <= 50 dimensions, preprocessing settings, orig data path(s), '
                    'orig file type\n')

    with open(exportFile, 'a') as f:
        f.write('{},"{}","{}",[{}],{}\n'.format(current_id,
                                                pathlib.Path(os.path.normpath(filePath)).as_posix(),
                                                pathlib.Path(os.path.normpath(settingsPath)).as_posix(),
                                                ";".join([pathlib.Path(os.path.normpath(p)).as_posix() for p in origDataPaths]),
                                                origDataType))

"""
Adds a new entry to the dataset list.
"""
def addToVisDataList(dataPath, settingsPath, preprocessingSettingsPath, current_id, exportFile, origDataPaths,
                     origDataType, preprocessedDataPath):
    if not os.path.exists(exportFile):
        # header
        with open(exportFile, 'w') as f:
            f.write('# orig id, path to csv with max 50 dimensions, path to settings, path to preprocessing settings, '
                    'orig data paths, preprocessing data path\n')

    with open(exportFile, 'a') as f:
        f.write('{},"{}","{}","{}",{},{},{}\n'.format(current_id,
                                                      pathlib.Path(os.path.normpath(dataPath)).as_posix(),
                                                      pathlib.Path(os.path.normpath(settingsPath)).as_posix(),
                                                      pathlib.Path(os.path.normpath(preprocessingSettingsPath)).as_posix(),
                                                      origDataPaths,
                                                      origDataType,
                                                      preprocessedDataPath))
