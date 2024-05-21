#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Preprocessing for multidimensional time series projections.
"""

import copy
import numpy as np
import os
import sklearn as sk

from dimRed import myTypes
from dimRed.myTypes import DimRedMethod, Preprocessing
import dimRed.dimRed as dimensionReduction
import dimRed.loadData as loadExample
import dimRed.save as save
import dimRed.settings.currentSettings as currentSettings
import dimRed.settings.dimRedTypesSettings as dimRedTypesSettings
import dimRed.settings.generalSettings as generalSettings
import dimRed.settings.pathSettings as pathSettings
import dimRed.settingsIO as settingsIO

"""
Data preparation:
Preprocessing for high-dimensional data: normalize/... data and reduce to 50 dimensions with PCA
"""
def main():
    currentPath = os.path.dirname(os.path.abspath(__file__))
    directories = loadExample.getDatasetPaths(pathSettings.datasetPath)

    for pathSettings.baseDir in directories:

        print("PROCESSING: " + pathSettings.baseDir)

        os.chdir(currentPath)
        os.chdir(os.path.abspath(pathSettings.baseDir))

        cS = currentSettings.SettingProperties()

        # read settings file and override settings
        settingsIO.extractPreprocessingSettings()
        settingsParams = copy.deepcopy(generalSettings.initialPCADimRedSettings[0].params)

        # load file with all examples and remember id -> (path, type of data)
        datasets = loadExample.getAllTrials(pathSettings.origDatasetPaths)

        # specify trials; all (empty list) or ids in list?
        if generalSettings.trial:
            datasets = [x for x in datasets if x in generalSettings.trial]

        for dataId, dataInfo in datasets.items():
            # LOAD DATA
            origDataPaths = dataInfo[0]
            origDataType = dataInfo[1]
            m, dataLengths, labels, width, height = loadExample.getTrialData(dataId, origDataPaths, origDataType, cS)

            count = 0
            for cS.ignoreFirstDimension in generalSettings.ignoreFirstDimension:
                for cS.everyXSample in generalSettings.everyXSample:

                    cS.initialPCADimRedSettings = dimRedTypesSettings.extractData({}, "PCA")

                    elements = list(settingsParams.keys())
                    for el in elements:
                        cS.initialPCADimRedSettings.params[el] = [settingsParams[el][0]]

                    tempSettings = copy.deepcopy(cS)
                    previousSettings = [tempSettings]
                    for el in elements:
                        new = []
                        for setting in previousSettings:
                            for x in settingsParams[el][1:]:
                                # for all changes
                                newSettings = copy.deepcopy(setting)
                                newSettings.initialPCADimRedSettings.params = copy.deepcopy(
                                    setting.initialPCADimRedSettings.params)
                                newSettings.initialPCADimRedSettings.params[el] = [x]
                                new.append(newSettings)
                        previousSettings += new

                    for cS.preprocessing in generalSettings.preprocessing:
                        for x in previousSettings:
                            x.preprocessing = cS.preprocessing
                            cS = x
                            cS.trial = str(dataId) + "-" + str(count)

                            Xs = m.copy()
                            numDim = m.shape[1]

                            # PREPROCESSING
                            Xs = preprocess(np.array(Xs), cS)

                            # REDUCE TO 50 DIMENSIONS WITH PCA (in case ths value is set)
                            if Xs.shape[0] > cS.initialPCADimRedSettings.params["n_components"][0]:  # TODO: just the first value is used
                                Xs = dimensionReduction.dimensionReduction(Xs, DimRedMethod.PCA,
                                                                           cS.initialPCADimRedSettings)

                            # SAVE DATA
                            if cS.preprocessing == Preprocessing.normalization:
                                preprocessingDir = pathSettings.normalizedPCADir
                                preprocessingString = "PCA50_normalization"

                            elif cS.preprocessing == Preprocessing.standardization:
                                preprocessingDir = pathSettings.standardizedPCADir
                                preprocessingString = "PCA50_standardization"

                            elif cS.preprocessing == Preprocessing.no:
                                preprocessingDir = pathSettings.origPCADir
                                preprocessingString = "PCA50_original"

                            elif cS.preprocessing == Preprocessing.standardizationAndNormalization:
                                preprocessingDir = pathSettings.standardizedAndNormalizedPCADir
                                preprocessingString = "PCA50_standardizationAndNormalization"

                            else:
                                continue

                            newFile, settingsPath = save.saveData(Xs, dataLengths, preprocessingDir,
                                                                  preprocessingString, cS, numDim)
                            save.addToPreprocessedDataList(pathSettings.preprocessedDataPaths, cS.trial,
                                                           newFile, settingsPath, origDataPaths, origDataType)

                            count += 1


"""
Preprocessing of data: normalization, standardization, ...
"""
def preprocess(x, cS):
    print("...preprocessing...")

    if cS.preprocessing == myTypes.Preprocessing.no:
        print("normalization skipped")
        return x
    if cS.preprocessing == myTypes.Preprocessing.normalization:
        print("normalization")
        return sk.preprocessing.normalize(x)
    if cS.preprocessing == myTypes.Preprocessing.standardization:
        print("standardization")
        return sk.preprocessing.scale(x)
    if cS.preprocessing == myTypes.Preprocessing.standardizationAndNormalization:
        print("standardizationAndNormalization")
        x = sk.preprocessing.scale(x)
        return sk.preprocessing.normalize(x)
    print("...preprocessing finished...")


if __name__ == '__main__':
    exit(main())
