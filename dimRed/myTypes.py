#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Specification of enums.
"""

from enum import Enum

"""
Supported dimensionality reduction methods.
"""
class DimRedMethod(Enum):
    tSNE = 0,
    PCA = 1,
    MDS = 2,
    LLE = 7,
    Isomap = 8,
    SE = 9,
    UMAP = 5

"""
Interpolation types.
"""
class SampleInterpolation(Enum):
    catmullRom = 0,
    line = 1,
    centripetalCatmullRom = 2

"""
Preprocessing mode.
"""
class Preprocessing(Enum):
    no = 0
    normalization = 1,
    standardization = 2,
    standardizationAndNormalization = 3
