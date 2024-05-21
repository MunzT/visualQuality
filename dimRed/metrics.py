#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Methods to support the calculation of different metrics.
"""

from scipy import stats
import math
import numpy as np

import dimRed.math as ma

# Metrics to calculate overall values for a whole dataset; can also be used locally for subsets
# (neighborhood or sliding window)

def normalizedStress(distances_2D, distances_50D):  # lists do not have to be normalized
    # 0 is best
    distances_2D = np.hstack(distances_2D)
    distances_50D = np.hstack(distances_50D)

    maxVal_2D = max(distances_2D)
    distances_2D = distances_2D / maxVal_2D
    maxVal_50D = max(distances_50D)
    distances_50D = distances_50D / maxVal_50D

    if maxVal_50D == 0:
        if maxVal_2D == 0:
            return 0
        return 1
    stress = np.sum(np.square(distances_2D - distances_50D)) / np.sum(np.square(distances_50D))
    return stress

def spearmanCorrelation(distances_2D, distances_50D):
    # values range from -1 to 1; 1 is best (positive correlation); -1 negative correlation
    distances_2D = np.hstack(distances_2D)
    distances_50D = np.hstack(distances_50D)

    if len(distances_2D) < 2:  # not enough values...
        return 0

    spearman, pvalue_spearman = stats.spearmanr(distances_50D, distances_2D)
    return spearman

def pearsonCorrelation(distances_2D, distances_50D):
    # values range from -1 to 1; 1 is best (positive correlation); -1 negative correlation
    distances_2D = np.hstack(distances_2D)
    distances_50D = np.hstack(distances_50D)

    if len(distances_2D) < 2:  # not enough values...
        return 0

    pearson, pvalue_pearson = stats.pearsonr(distances_50D, distances_2D)

    return pearson

def kendallCorrelation(distances_2D, distances_50D):
    # values range from -1 to 1; 1 is best (positive correlation); -1 negative correlation
    distances_2D = np.hstack(distances_2D)
    distances_50D = np.hstack(distances_50D)

    if len(distances_2D) < 2:  # not enough values...
        return 0

    kendall, pvalue_kendall = stats.kendalltau(distances_50D, distances_2D)

    return kendall

def trustworthiness(neighbors_2D, neighbors_50D, k=7, overrideN=0):  # 1 is best
    N = neighbors_2D.shape[0]
    nearestNeighborValue = 0
    for i in range(N):
        kNearestNeighbors_i_2D = neighbors_2D[i, 1:k+1]
        kNearestNeighbors_i_50D = neighbors_50D[i, 1:k+1]
        U_i = np.setdiff1d(kNearestNeighbors_i_50D, kNearestNeighbors_i_2D, assume_unique=True)
        sumRank = 0
        for j in U_i:
            rank_i_j = int(np.where(neighbors_2D[i] == j)[0] + 1)
            sumRank += rank_i_j - k

        nearestNeighborValue += sumRank

    N = max(N, overrideN)
    return float((1 - (2 / (N * k * (2 * N - 3 * k - 1)) * nearestNeighborValue)))

def continuity(neighbors_2D, neighbors_50D, k=7, overrideN=0):  # 1 is best

    N = neighbors_2D.shape[0]

    nearestNeighborValue = 0
    for i in range(N):
        kNearestNeighbors_i_2D = neighbors_2D[i, 1:k+1]
        kNearestNeighbors_i_50D = neighbors_50D[i, 1:k+1]
        U_i = np.setdiff1d(kNearestNeighbors_i_2D, kNearestNeighbors_i_50D, assume_unique=True)

        sumRank = 0
        for j in U_i:
            rank_i_j = int(np.where(neighbors_50D[i] == j)[0] + 1)
            sumRank += rank_i_j - k
        nearestNeighborValue += sumRank

    N = max(N, overrideN)
    return float((1 - (2 / (N * k * (2 * N - 3 * k - 1)) * nearestNeighborValue)))

# Metrics to calculate values for each sample
def RMSEForAllSamples(distances_2D, distances_50D):  # local mean square error
    n = len(distances_2D)

    # normalize values
    distances_2D = ma.minMaxScale(distances_2D, 0, 1)
    distances_50D = ma.minMaxScale(distances_50D, 0, 1)

    values = []
    for i in range(n):
        value = 0
        for j in range(n):
            value += (distances_2D[j][j] - distances_50D[i][j]) ** 2
        values.append(math.sqrt(value / n))

    return values

def kruskalStressForAllSamples(distances_2D, distances_50D):
    n = len(distances_2D)

    # normalize values
    distances_2D = ma.minMaxScale(distances_2D, 0, 1)
    distances_50D = ma.minMaxScale(distances_50D, 0, 1)

    values = []
    for i in range(n):
        value1 = 0
        for j in range(n):
            value1 += (distances_2D[i][j] - distances_50D[i][j]) ** 2
        value2 = 0
        for j in range(n):
            value2 += distances_2D[i][j] ** 2

        values.append(math.sqrt(value1 / value2))
    return values

def neighborhoodLossForAllSamplse(neighbors_2D, neighbors_50D, k):
    n = len(neighbors_2D)

    values = []
    for i in range(n):
        kNearestNeighbors_i_2D = neighbors_2D[i, 1:k + 1]
        kNearestNeighbors_i_50D = neighbors_50D[i, 1:k + 1]

        intersection = np.intersect1d(kNearestNeighbors_i_2D, kNearestNeighbors_i_50D, assume_unique=True)

        values.append(1 - abs(len(intersection)) / k)
    return values
