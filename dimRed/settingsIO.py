#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Create strings from current settings.
"""

import toml

from dimRed.settings import currentSettings
from dimRed.settings import dimRedTypesSettings
from dimRed.settings import generalSettings
from dimRed.settings import interpolationSettings
from dimRed.settings import pathSettings
from dimRed import myTypes

"""
Create a string with settings information (can be used as settings file which can also be imported).
"""
def settingsMetadata(cS):
    d = {}
    d["TrialID"] = cS.trial
    d["EveryXSample"] = cS.everyXSample
    d["IgnoreFirstDimension"] = cS.ignoreFirstDimension
    d["DimRed"] = cS.dimRedMethod.name
    d[cS.dimRedMethod.name] = dict((k, v[0]) for k, v in cS.dimRedSettings.params.items() if k in cS.dimRedSettings.customParameterValues)
    d["UseSubsampling"] = cS.subsampleInHighDimSpace
    d["SubsamplingCount"] = cS.subsampleCount
    d["SubsamplingCountFixed"] = cS.subsampleCountFixed
    d["SubsamplingType"] = cS.subsampleType.name
    d["UseSubsamplesForEmbedding"] = cS.useSubsamplesForEmbedding

    return toml.dumps(d)

def settingsPreprocessing(cS, origDims):
    d = {}
    d["TrialID"] = cS.trial
    d["EveryXSample"] = cS.everyXSample
    d["IgnoreFirstDimension"] = cS.ignoreFirstDimension
    d["DimRed"] = cS.dimRedMethod.name
    d[cS.dimRedMethod.name] = dict((k, v[0]) for k, v in cS.initialPCADimRedSettings.params.items() if k in
                                   cS.initialPCADimRedSettings.customParameterValues)
    d["Dims"] = cS.initialPCADimRedSettings.params["n_components"][0]
    d["OrigDims"] = origDims
    d["Preprocessing"] = cS.preprocessing.name

    print(toml.dumps(d))
    print(str(toml.dumps(d)))

    return toml.dumps(d)

"""
Update settings according to the values given in the struct d.
"""
def changeSettings(d, cS):
    # Settings
    currentSettings.trial = d["TrialID"] if "TrialID" in d and "trial" else cS.trial
    currentSettings.everyXSample = \
        d["EveryXSample"] if "EveryXSample" in d else cS.everyXSample
    currentSettings.ignoreFirstDimension = \
        d["IgnoreFirstDimension"] if "IgnoreFirstDimension" in d else cS.ignoreFirstDimension
    currentSettings.dimRedMethod = myTypes.DimRedMethod[d["DimRed"]] if "DimRed" in d else cS.dimRedMethod

    currentSettings.dimRedSettings = \
        dimRedTypesSettings.extractData(d[currentSettings.dimRedMethod.name], currentSettings.dimRedMethod.name)

    currentSettings.subsampleInHighDimSpace = \
        d["UseSubsampling"] if "UseSubsampling" in d else cS.subsampleInHighDimSpace
    currentSettings.subsampleCount = \
        d["SubsamplingCount"] if "SubsamplingCount" in d else cS.subsampleCount
    currentSettings.subsampleCountFixed = \
        d["SubsamplingCountFixed"] if "SubsamplingCountFixed" in d else cS.subsampleCountFixed
    cS.subsampleType = \
        myTypes.SampleInterpolation[d["SubsamplingType"]] if "SubsamplingType" in d else cS.subsampleType
    currentSettings.useSubsamplesForEmbedding = \
        d["UseSubsamplingForEmbedding"] if "UseSubsamplingForEmbedding" in d else cS.useSubsamplesForEmbedding

"""
Creates a string for the directory name.
"""
def settingsDirName(cS, newName):

    # 5 substrings:
    # trial and properties
    # initial PCA
    # Dim Red Method
    # Subsampling + Embedding
    # Drawing

    trialString = str(newName) +\
                  ("-IgnoreFirstDim" if cS.ignoreFirstDimension else "") + \
                  ("-Every{}samples".format(cS.everyXSample) if cS.everyXSample != 1 else "")

    dimRedSettings = "DimRed-" + dimRedTypesSettings.settingsToStringForFilePath(cS.dimRedMethod,
                                                                                 cS.dimRedSettings)

    subsamplingString = "S{}{}".format(str(cS.subsampleInHighDimSpace),
                                       ("-T" + cS.subsampleType.name +
                                        ("-CVarying" if not cS.subsampleCountFixed else "-C" + str(cS.subsampleCount)))
                                       if cS.subsampleInHighDimSpace else "") + \
                        ("-EmbeddingFromAllSamples" if cS.useSubsamplesForEmbedding and
                         cS.subsampleInHighDimSpace else
                         "-EmbeddingFromMainSamples" if cS.subsampleInHighDimSpace else "")

    return "_".join(filter(None, [trialString, dimRedSettings, subsamplingString]))

"""
Extract settings for batch processing.
"""
def extractSettings():
    settings = getSettings(pathSettings.settingsForVis)

    generalSettings.trial = settings["general"]["trial"] if "general" in settings and \
        "trial" in settings["general"] else generalSettings.trial
    generalSettings.everyXSample = \
        settings["general"]["everyXSample"] if "general" in settings and \
        "everyXSample" in settings["general"] else generalSettings.everyXSample
    generalSettings.ignoreFirstDimension = \
        settings["general"]["ignoreFirstDimension"] if "general" in settings and \
        "ignoreFirstDimension" in settings["general"] else generalSettings.ignoreFirstDimension
    generalSettings.dimRedMethod = \
        [myTypes.DimRedMethod[x] for x in settings["general"]["dimRedMethod"]] if "general" in settings and \
        "dimRedMethod" in settings["general"] else generalSettings.dimRedMethod

    generalSettings.dimRedSettings = \
        [dimRedTypesSettings.extractData(settings[y.name] if y.name in settings else {}, y.name)
         for x, y in enumerate(generalSettings.dimRedMethod)]

    generalSettings.continuousLabels = \
        settings["export"]["continuousLabels"] if "export" in settings and \
        "continuousLabels" in settings["export"] else generalSettings.continuousLabels

    interpolationSettings.subsampleInHighDimSpace = \
        settings["subsampling"]["subsampleInHighDimSpace"] if "subsampling" in settings and \
        "subsampleInHighDimSpace" in settings["subsampling"] else interpolationSettings.subsampleInHighDimSpace
    interpolationSettings.subsampleCount = \
        settings["subsampling"]["subsampleCount"] if "subsampling" in settings and \
        "subsampleCount" in settings["subsampling"] else interpolationSettings.subsampleCount
    interpolationSettings.subsampleCountFixed = \
        settings["subsampling"]["subsampleCountFixed"] if "subsampling" in settings and \
        "subsampleCountFixed" in settings["subsampling"] else interpolationSettings.subsampleCountFixed
    interpolationSettings.subsampleType = \
        [myTypes.SampleInterpolation[x] for x in settings["subsampling"]["subsampleType"]] if \
        "subsampling" in settings and "subsampleType" in settings["subsampling"] else interpolationSettings.subsampleType
    interpolationSettings.useSubsamplesForEmbedding = \
        settings["subsampling"]["useSubsamplesForEmbedding"] if "subsampling" in settings and \
                                                                "useSubsamplesForEmbedding" in settings["subsampling"] \
                                                                else interpolationSettings.useSubsamplesForEmbedding

"""
Extract settings for batch preprocessing.
"""
def extractPreprocessingSettings():
    settings = getSettings(pathSettings.settingsForPreprocessing)

    generalSettings.trial = settings["general"]["trial"] if "general" in settings and \
                                                            "trial" in settings["general"] else generalSettings.trial
    generalSettings.everyXSample = \
        settings["general"]["everyXSample"] if "general" in settings and \
                                               "everyXSample" in settings["general"] else generalSettings.everyXSample
    generalSettings.ignoreFirstDimension = \
        settings["general"]["ignoreFirstDimension"] if "general" in settings and \
                                                       "ignoreFirstDimension" in settings["general"] else \
                                                       generalSettings.ignoreFirstDimension

    generalSettings.initialPCADimRedSettings = \
        [dimRedTypesSettings.extractData(settings["PCA"], "PCA")]

    generalSettings.preprocessing = [myTypes.Preprocessing[x] for x in settings["general"]["preprocessing"]]  \
        if "general" in settings and \
        "preprocessing" in settings["general"] \
        else generalSettings.preprocessing

def getSettings(filePath):
    data = toml.load(filePath)

    return data
