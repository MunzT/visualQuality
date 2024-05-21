#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
General functions for metric calculations.
"""

from sklearn import metrics
from sklearn.neighbors import NearestNeighbors
import numpy as np

import dimRed.debugData as debugData

def sortNearestNeighbors(data):
    data = data.astype(np.float64)
    distances, neighbors = NearestNeighbors(n_neighbors=len(data), metric='euclidean',
                                            algorithm='ball_tree').fit(data).kneighbors(data)

    distances = distances / np.amax(distances)

    return distances, neighbors

def getPairwiseDistances(data):
    return metrics.pairwise_distances(data)

def getMax(data):  # data can have different sub shapes
    return max(sub.max() for sub in data)

def getMin(data):  # data can have different sub shapes
    return min(sub.min() for sub in data)

def minMaxScale(data, newMin=0, newMax=1):
    minVal = getMin(data)
    maxVal = getMax(data)

    epsilon = 0.000001
    if abs(maxVal - minVal) < epsilon:
        return data - data

    return (data - minVal) * (newMax - newMin) / (maxVal - minVal) + newMin

def getDistanceDifferences(distances_50D, distances_2D):
    return distances_2D - distances_50D

def getDistancesToNextSample(data_structure, pairwise_distances_2D, pairwise_distances_50D):
    # calculate distances/...
    distanceToNextSample_2D = []  # distance for vis
    distanceToNextSample_50D = []  # speed
    c = 0
    for i in range(len(data_structure)):
        distanceToNextSample_2D_i = []
        distanceToNextSample_50D_i = []
        for j in range(len(data_structure[i]) - 1):
            distanceToNextSample_2D_i.append(pairwise_distances_2D[c][c + 1])
            distanceToNextSample_50D_i.append(pairwise_distances_50D[c][c + 1])
            c += 1
            if j == len(data_structure[i]) - 1 - 1:
                c += 1

        distanceToNextSample_2D.append(np.asarray(distanceToNextSample_2D_i))
        distanceToNextSample_50D.append(np.asarray(distanceToNextSample_50D_i))

    distanceToNextSample_2D = np.asarray(distanceToNextSample_2D)
    distanceToNextSample_50D = np.asarray(distanceToNextSample_50D)

    debugData.debugData(distanceToNextSample_2D, "distanceToNextSample_2D")
    debugData.debugData(distanceToNextSample_50D, "distanceToNextSample_50D")

    return distanceToNextSample_2D, distanceToNextSample_50D
