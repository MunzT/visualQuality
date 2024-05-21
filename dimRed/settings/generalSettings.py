#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
General settings for preprocessing and visualization.
"""

from dimRed.settings import dimRedTypesSettings
from dimRed import myTypes

trial = []
everyXSample = [1]
ignoreFirstDimension = [False]
continuousLabels = [True]
dimRedMethod = [myTypes.DimRedMethod.PCA]
dimRedSettings = [dimRedTypesSettings.PcaSettings()]

initialPCADimRedSettings = [dimRedTypesSettings.PcaSettings()]

preprocessing = [myTypes.Preprocessing.normalization, myTypes.Preprocessing.standardization,
                 myTypes.Preprocessing.no,
                 myTypes.Preprocessing.standardizationAndNormalization]
