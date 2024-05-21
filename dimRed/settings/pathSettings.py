#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Default file names and paths.
"""

import os

# file containing current data set paths
datasetPath = r"datasets.txt"

# base dir for data
baseDir = r""

# read by main_PCA50
origDatasetPaths = "origDatasets.csv"

# errors, ...
logDir = "log"

# preprocessed data paths
preprocessedDataPaths = "2_preprocessedData.csv"
visDataPaths = "3_visData.csv"

preprocessedDataDir = "2_preprocessedData"
visDataDir = "3_visData"
imageDir = "3_preview"
statDir = "3_statistics"

settingsForVis = "visData.toml"
settingsForPreprocessing = "preprocessData.toml"

# created by main_PCA50
normalizedPCADir = os.path.join(preprocessedDataDir, "normalization")
standardizedPCADir = os.path.join(preprocessedDataDir, "standardization")
origPCADir = os.path.join(preprocessedDataDir, "original")
standardizedAndNormalizedPCADir = os.path.join(preprocessedDataDir, "standardizationAndNormalization")
