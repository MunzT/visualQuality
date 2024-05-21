#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Currently used settings.
"""

from dimRed.settings import dimRedTypesSettings
from dimRed import myTypes

class SettingProperties:
    # generalSettings
    trial = "0"
    everyXSample = 1
    ignoreFirstDimension = False
    dimRedMethod = myTypes.DimRedMethod.PCA
    continuousLabels = True

    # dimRedTypesSettings
    dimRedSettings = dimRedTypesSettings.PcaSettings()

    # interpolationSettings
    subsampleInHighDimSpace = False
    subsampleCount = 5
    subsampleCountFixed = True
    subsampleType = myTypes.SampleInterpolation.catmullRom
    useSubsamplesForEmbedding = False

    # preprocessing
    preprocessing = None
    initialPCADimRedSettings = dimRedTypesSettings.PcaSettings()

    def printData(self):
        print(self.trial)
        print(self.everyXSample)
        print(self.ignoreFirstDimension)
        print(self.dimRedMethod.name)
        print(self.continuousLabels)

        # dimRedTypesSettings
        print("{}:{}".format(self.dimRedMethod.name,  dimRedTypesSettings.usedSettingsToString(self.dimRedSettings)))

        # interpolationSettings
        print(self.subsampleInHighDimSpace)
        print(self.subsampleCount)
        print(self.subsampleCountFixed)
        print(self.subsampleType)
        print(self.useSubsamplesForEmbedding)

        # preprocessing
        print(self.preprocessing)
        print("Initial settings:{}".format(dimRedTypesSettings.usedSettingsToString(self.initialPCADimRedSettings)))
