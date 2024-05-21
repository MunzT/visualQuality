#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Generate 2D projections of high dimensional data to bve explored in the visualization system.
"""

import copy
import numpy as np
import os

from dimRed.myTypes import DimRedMethod
import dimRed.dimRed as dimensionReduction
import dimRed.draw as draw
import dimRed.interpolate as interpolate
import dimRed.loadData as loadExample
import dimRed.save as save
import dimRed.settings.currentSettings as currentSettings
import dimRed.settings.dimRedTypesSettings as dimRedTypesSettings
import dimRed.settings.generalSettings as generalSettings
import dimRed.settings.interpolationSettings as interpolationSettings
import dimRed.settings.pathSettings as pathSettings
import dimRed.settingsIO as settingsIO

"""
Applies dimensionality reduction to the data set (firs, to reduce to 50 dimensions, then to 2) and draws the plot.
"""
def dimensionReductionAndPlot(XsList, labelsList, cS, preprocessingSettings):
    mainSamplesList = []
    m_originalList = []

    for i in range(len(XsList)):
        Xs = XsList[i]
        m_original = Xs.copy()
        m_originalList.append(m_original)

        # interpolation in high dim
        XsList[i], mainSamples = interpolate.addInterpolatedSamples(Xs, cS)

        mainSamplesList.append(mainSamples)

    # merge different lists
    Xs = np.concatenate(XsList, axis=0)
    m_original = np.concatenate(m_originalList, axis=0)

    # PCA/MDS/t-SNE,...
    if cS.subsampleInHighDimSpace and not cS.useSubsamplesForEmbedding:
        if (cS.dimRedMethod == DimRedMethod.PCA or
                cS.dimRedMethod == DimRedMethod.UMAP):
            X_embedded = dimensionReduction.dimensionReductionForEmbedding(m_original, Xs, cS.dimRedMethod,
                                                                           cS.dimRedSettings, 2)
        else:
            return "", "", ""  # not possible to create result for settings
    else:
        print("no subsampling")
        X_embedded = dimensionReduction.dimensionReduction(Xs, cS.dimRedMethod, cS.dimRedSettings, 2)

    s = 0
    X_embeddedLists = []
    for i in range(len(mainSamplesList)):
        X_embeddedLists.append(X_embedded[s:s + len(mainSamplesList[i])])
        s += len(mainSamplesList[i])

    # intersections/summary, ...
    dataPath, settingsPath, preprocessingSettingsPath = \
        save.saveCoordinatesOfEmbedding(X_embeddedLists, mainSamplesList, labelsList, cS, preprocessingSettings, cS.trial)

    # finally: draw
    draw.plotFigure(X_embeddedLists, mainSamplesList, labelsList, cS, cS.trial)

    return dataPath, settingsPath, preprocessingSettingsPath


def processData(m, labels, cS, preprocessingSettings, origDataPaths, origDataType, preprocessedDataPath):
    print("***************************************")
    print(settingsIO.settingsMetadata(cS))
    print("***************************************")

    dataPath, settingsPath, preprocessingSettingsPath = dimensionReductionAndPlot(m, labels, cS, preprocessingSettings)

    if dataPath == "":  # it was not possible to create results for the options
        return False

    save.addToVisDataList(dataPath, settingsPath, preprocessingSettingsPath, cS.trial, pathSettings.visDataPaths,
                          origDataPaths, origDataType, preprocessedDataPath)
    return True


"""
Main function.
"""
def main():
    currentPath = os.path.dirname(os.path.abspath(__file__))

    directories = loadExample.getDatasetPaths(pathSettings.datasetPath)

    for pathSettings.baseDir in directories:

        os.chdir(currentPath)
        os.chdir(os.path.abspath(pathSettings.baseDir))

        cS = currentSettings.SettingProperties()

        # read files with trial paths
        datasets = loadExample.getAllPreprocessedTrials(pathSettings.preprocessedDataPaths)

        # read settings file and override settings
        settingsIO.extractSettings()

        # specify trials; all (empty list) or ids in list?
        if generalSettings.trial:
            datasets = [x for x in datasets if x in generalSettings.trial]

        print("OVERVIEW:")
        print(datasets)
        print(generalSettings.everyXSample)
        print(generalSettings.ignoreFirstDimension)
        print(generalSettings.continuousLabels)
        print(interpolationSettings.subsampleInHighDimSpace)
        print(interpolationSettings.subsampleCount)
        print(interpolationSettings.subsampleCountFixed)
        print(interpolationSettings.subsampleType)
        print(interpolationSettings.useSubsamplesForEmbedding)
        print(generalSettings.dimRedMethod)
        for i in generalSettings.dimRedSettings:
            print(dimRedTypesSettings.usedSettingsToString(i))

        # iterate over trials and load trial
        for cS.trial in datasets:
            m, labels = loadExample.getPreprocessedDataForDimRed(datasets[cS.trial][0], cS)
            count = 0
            for cS.everyXSample in generalSettings.everyXSample:
                for cS.ignoreFirstDimension in generalSettings.ignoreFirstDimension:
                    for cS.continuousLabels in generalSettings.continuousLabels:
                        for cS.subsampleInHighDimSpace in interpolationSettings.subsampleInHighDimSpace:
                            subsampling = cS.subsampleInHighDimSpace
                            for cS.subsampleCountFixed in interpolationSettings.subsampleCountFixed if \
                                    subsampling else [interpolationSettings.subsampleCountFixed[0]]:
                                for cS.subsampleCount in interpolationSettings.subsampleCount if \
                                        subsampling and cS.subsampleCountFixed else [interpolationSettings.subsampleCount[0]]:
                                    for cS.subsampleType in interpolationSettings.subsampleType if \
                                            subsampling else [interpolationSettings.subsampleType[0]]:
                                        for cS.useSubsamplesForEmbedding in interpolationSettings.useSubsamplesForEmbedding if \
                                                subsampling else [interpolationSettings.useSubsamplesForEmbedding[0]]:
                                            dimRedIndex = -1
                                            for cS.dimRedMethod in generalSettings.dimRedMethod:

                                                cS.dimRedSettings = dimRedTypesSettings.extractData({}, cS.dimRedMethod.name)

                                                dimRedIndex += 1

                                                settingsParams = copy.deepcopy(generalSettings.dimRedSettings[dimRedIndex].params)

                                                elements = list(settingsParams.keys())

                                                cS.dimRedSettings.customParameterValues = \
                                                    copy.deepcopy(generalSettings.dimRedSettings[dimRedIndex].customParameterValues)
                                                cS.dimRedSettings.params = \
                                                    copy.deepcopy(generalSettings.dimRedSettings[dimRedIndex].params)

                                                # initialize
                                                for el in elements:
                                                    cS.dimRedSettings.params[el] = [settingsParams[el][0]]

                                                tempSettings = copy.deepcopy(cS)
                                                previousSettings = [tempSettings]

                                                for el in elements:
                                                    new = []
                                                    for setting in previousSettings:
                                                        for x in settingsParams[el][1:]:
                                                            # for all changes
                                                            newSettings = copy.deepcopy(setting)
                                                            newSettings.dimRedSettings.params = \
                                                                copy.deepcopy(setting.dimRedSettings.params)
                                                            newSettings.dimRedSettings.params[el] = [x]
                                                            new.append(newSettings)
                                                    previousSettings += new

                                                for x in previousSettings:
                                                    x.trial = str(cS.trial) + "-" + str(count)

                                                    success = processData(m.copy(), labels.copy(), x, datasets[cS.trial][1],
                                                                          datasets[cS.trial][2],
                                                                          datasets[cS.trial][3],
                                                                          datasets[cS.trial][0])
                                                    if success:
                                                        count += 1


if __name__ == '__main__':
    exit(main())
