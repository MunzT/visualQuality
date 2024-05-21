#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Settings for dimensionality reduction.
"""

from sklearn import manifold, decomposition
import inspect
import umap

"""
Classes for different dimensionality reduction technique with different settings.
"""

def getDefaultParameters(function):
    signature = inspect.signature(function)
    return {
        k: [v.default]
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

def getFirstElements(el):
    el = el.copy()
    for k, v in el.items():
        el[k] = v[0]
    return el

class PcaSettings:  # can be used without parameters
    params = getDefaultParameters(decomposition.PCA)
    customParameterValues = []

    params["random_state"] = [42]

class MdsSettings:
    params = getDefaultParameters(manifold.MDS)
    customParameterValues = []

    params["random_state"] = [42]
    params["dissimilarity"] = ["euclidean"]
    params["metric"] = [True]

class TSNESettings:
    params = getDefaultParameters(manifold.TSNE)
    customParameterValues = []

    params["random_state"] = [42]
    params["metric"] = ["euclidean"]

class UmapSettings:
    params = getDefaultParameters(umap.UMAP)
    customParameterValues = []

    params["random_state"] = [42]
    params["metric"] = ["euclidean"]

class LleSettings:
    params = getDefaultParameters(manifold.LocallyLinearEmbedding)
    customParameterValues = []

    params["random_state"] = [42]

class IsomapSettings:
    params = getDefaultParameters(manifold.Isomap)
    customParameterValues = []

class SeSettings:
    params = getDefaultParameters(manifold.SpectralEmbedding)
    customParameterValues = []

    params["random_state"] = [42]

def extractData(settingsDict, dimRedType):
    settings = None
    if dimRedType == "PCA":
        settings = PcaSettings()
    elif dimRedType == "MDS":
        settings = MdsSettings()
    elif dimRedType == "tSNE":
        settings = TSNESettings()
    elif dimRedType == "UMAP":
        settings = UmapSettings()
    elif dimRedType == "LLE":
        settings = LleSettings()
    elif dimRedType == "Isomap":
        settings = IsomapSettings()
    elif dimRedType == "SE":
        settings = SeSettings()

    for key, value in settingsDict.items():
        if key in settings.params:
            settings.params[key] = value
            settings.customParameterValues.append(key)

    return settings

def usedSettingsToString(settings):
    return str(dict((k, v) for k, v in settings.params.items() if k in settings.customParameterValues))

def settingsToStringForFilePath(dimRedMethod, settings):
    elements = [(k, v) for k, v in settings.params.items() if k in settings.customParameterValues]
    return "{}_".format(dimRedMethod.name) + "-".join(["{}_{}".format(x[0], str(x[1])[1:-1]).
                                                      replace("\"", "").replace("'", "") for x in elements])


dimRedSettings = [PcaSettings()]
