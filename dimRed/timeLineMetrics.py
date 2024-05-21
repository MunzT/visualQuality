#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Metrics for line/samples of temporal projections.
"""

import numpy as np
import statistics

def temporalPosition(data_structure, dataType):
    timePosition = []
    for i in range(len(data_structure)):
        timePosition_i = []
        for j in range(len(data_structure[i])):
            if dataType == "samples":
                timePosition_i.append(j / (len(data_structure[i]) - 1))
            elif dataType == "lines":
                timePosition_i.append(j / (len(data_structure[i]) - 2))
        if dataType == "samples":
            timePosition.append(np.asarray(timePosition_i))
        elif dataType == "lines":
            timePosition.append(np.asarray(timePosition_i[:-1]))
    return timePosition

def equalValues(data_structure, value, dataType):
    eqValues = []
    for i in range(len(data_structure)):
        equalValues_i = []
        for j in range(len(data_structure[i])):
            equalValues_i.append(value)

        if dataType == "samples":
            eqValues.append(np.asarray(equalValues_i))
        elif dataType == "lines":
            eqValues.append(np.asarray(equalValues_i[:-1]))
    return eqValues

# for local neighborhood of samples
def localNeighborhoodApproachMetricForSamples(data_structure, pairwise_distances_2D, pairwise_distances_50D,
                                              nn_neighbors_50D, maxNumberOfNeighbors, metric):
    localErrorsWithNeighborhood = []

    c_j = 0
    for i in range(len(data_structure)):
        localErrorsWithNeighborhood_i = []
        for j in range(len(data_structure[i])):
            numberNeighbors = min(maxNumberOfNeighbors, len(pairwise_distances_2D[c_j]))
            localNeighbors_50D = nn_neighbors_50D[c_j][:numberNeighbors]

            subData2D = np.asarray([pairwise_distances_2D[c_j][x] for x in localNeighbors_50D])
            subData50D = np.asarray([pairwise_distances_50D[c_j][x] for x in localNeighbors_50D])

            value = metric(subData2D, subData50D)

            localErrorsWithNeighborhood_i.append(value)
            c_j += 1

        localErrorsWithNeighborhood.append(np.asarray(localErrorsWithNeighborhood_i))
    localErrorsWithNeighborhood = np.asarray(localErrorsWithNeighborhood)
    return localErrorsWithNeighborhood

def localNeighborhoodApproachMetricForSamples2(nn_neighbors_2D, nn_neighbors_50D, maxNumberOfNeighbors, metric,
                                               oneMinus=True):
    localErrorsWithNeighborhood = []

    c_j = 0
    for i in range(len(nn_neighbors_50D)):
        numberNeighbors = min(maxNumberOfNeighbors, len(nn_neighbors_2D))
        localNeighbors_50D = nn_neighbors_50D[c_j][:numberNeighbors]

        subData2D = np.asarray([nn_neighbors_2D[x] for x in localNeighbors_50D])
        subData50D = np.asarray([nn_neighbors_50D[x] for x in localNeighbors_50D])

        if oneMinus:
            value = 1 - metric(subData2D, subData50D, numberNeighbors, nn_neighbors_2D.shape[0])
        else:
            value = metric(subData2D, subData50D, numberNeighbors, nn_neighbors_2D.shape[0])

        localErrorsWithNeighborhood_i = value

        c_j += 1

        localErrorsWithNeighborhood.append(localErrorsWithNeighborhood_i)

    localErrorsWithNeighborhood = np.asarray([localErrorsWithNeighborhood])
    return localErrorsWithNeighborhood

def slidingWindowApproachMetricForSamples(data_structure, distanceToNextSample_2D, distanceToNextSample_50D,
                                          slidingWindowSize, metric):

    localErrorsWithSlidingWindow = []
    for i in range(len(data_structure)):
        localErrorsWithSlidingWindow_i = []
        for j in range(len(data_structure[i])):
            subData2D = distanceToNextSample_2D[i][max(0, int(j - slidingWindowSize / 2.0)):
                                                   min(int(j + slidingWindowSize / 2.0), len(data_structure[i]) + 1)]
            subData50D = distanceToNextSample_50D[i][max(0, int(j - slidingWindowSize / 2.0)):
                                                     min(int(j + slidingWindowSize / 2.0), len(data_structure[i]) + 1)]

            localError = metric(subData2D, subData50D)

            localErrorsWithSlidingWindow_i.append(localError)

        localErrorsWithSlidingWindow.append(np.asarray(localErrorsWithSlidingWindow_i))

    return np.asarray(localErrorsWithSlidingWindow)

def slidingWindowApproachMetricForSamples2(nn_neighbors_2D, nn_neighbors_50D, slidingWindowSize, metric,
                                           oneMinus=True):
    localErrorsWithSlidingWindow = []
    for i in range(len(nn_neighbors_2D)):
        subData2D = nn_neighbors_2D[max(0, int(i - slidingWindowSize / 2.0)):min(int(i + slidingWindowSize / 2.0),
                                                                                 len(nn_neighbors_2D) + 1)]
        subData50D = nn_neighbors_50D[max(0, int(i - slidingWindowSize / 2.0)):min(int(i + slidingWindowSize / 2.0),
                                                                                   len(nn_neighbors_2D) + 1)]

        if oneMinus:
            localError = 1 - metric(subData2D, subData50D, slidingWindowSize, nn_neighbors_2D.shape[0])
        else:
            localError = metric(subData2D, subData50D, slidingWindowSize, nn_neighbors_2D.shape[0])

        localErrorsWithSlidingWindow_i = localError

        localErrorsWithSlidingWindow.append(localErrorsWithSlidingWindow_i)

    return np.asarray([localErrorsWithSlidingWindow])

# currently used
def localNeighborhoodApproachForSamples_50D(data_structure, pairwise_distances_2D, pairwise_distances_50D,
                                            maxNumberOfNeighbors, nn_neighbors_50D):
    localErrorsWithNeighborhood = []

    c_j = 0
    for i in range(len(data_structure)):
        localErrorsWithNeighborhood_i = []
        for j in range(len(data_structure[i])):
            numberNeighbors = min(maxNumberOfNeighbors, len(pairwise_distances_2D[c_j]))

            localNeighbors_50D = nn_neighbors_50D[c_j][:numberNeighbors]

            distancesToNeighbors_2D = np.asarray([pairwise_distances_2D[c_j][x] for x in localNeighbors_50D])
            distancesToNeighbors_50D = np.asarray([pairwise_distances_50D[c_j][x] for x in localNeighbors_50D])

            sum_2D = np.sum(distancesToNeighbors_2D) / len(distancesToNeighbors_2D)
            sum_50D = np.sum(distancesToNeighbors_50D) / len(distancesToNeighbors_50D)

            value = sum_2D - sum_50D

            localErrorsWithNeighborhood_i.append(value)
            c_j += 1
        localErrorsWithNeighborhood.append(np.asarray(localErrorsWithNeighborhood_i))
    localErrorsWithNeighborhood = np.asarray(localErrorsWithNeighborhood)
    return localErrorsWithNeighborhood

def localNeighborhoodApproachForSamples_2D(data_structure, pairwise_distances_2D, pairwise_distances_50D,
                                           maxNumberOfNeighbors, nn_neighbors_2D):
    localErrorsWithNeighborhood = []

    c_j = 0
    for i in range(len(data_structure)):
        localErrorsWithNeighborhood_i = []
        for j in range(len(data_structure[i])):
            numberNeighbors = min(maxNumberOfNeighbors, len(pairwise_distances_2D[c_j]))

            localNeighbors_2D = nn_neighbors_2D[c_j][:numberNeighbors]

            distancesToNeighbors_2D = np.asarray([pairwise_distances_2D[c_j][x] for x in localNeighbors_2D])
            distancesToNeighbors_50D = np.asarray([pairwise_distances_50D[c_j][x] for x in localNeighbors_2D])

            sum_2D = np.sum(distancesToNeighbors_2D) / len(distancesToNeighbors_2D)
            sum_50D = np.sum(distancesToNeighbors_50D) / len(distancesToNeighbors_50D)

            value = sum_2D - sum_50D

            localErrorsWithNeighborhood_i.append(value)
            c_j += 1
        localErrorsWithNeighborhood.append(np.asarray(localErrorsWithNeighborhood_i))
    localErrorsWithNeighborhood = np.asarray(localErrorsWithNeighborhood)
    return localErrorsWithNeighborhood

def localNeighborhoodApproachForSamples_Combined(data_structure, pairwise_distances_2D, pairwise_distances_50D,
                                                 maxNumberOfNeighbors, nn_neighbors_2D, nn_neighbors_50D):
    localErrorsWithNeighborhood = []

    c_j = 0
    for i in range(len(data_structure)):
        localErrorsWithNeighborhood_i = []
        for j in range(len(data_structure[i])):
            numberNeighbors = min(maxNumberOfNeighbors, len(pairwise_distances_2D[c_j]))

            localNeighbors_50D = nn_neighbors_50D[c_j][:numberNeighbors]
            localNeighbors_2D = nn_neighbors_2D[c_j][:numberNeighbors]

            intersection = np.intersect1d(localNeighbors_2D, localNeighbors_50D, assume_unique=False)

            distancesToNeighbors_2D = np.asarray([pairwise_distances_2D[c_j][x] for x in intersection])
            distancesToNeighbors_50D = np.asarray([pairwise_distances_50D[c_j][x] for x in intersection])

            sum_2D = np.sum(distancesToNeighbors_2D) / len(distancesToNeighbors_2D)
            sum_50D = np.sum(distancesToNeighbors_50D) / len(distancesToNeighbors_50D)

            value = sum_2D - sum_50D

            localErrorsWithNeighborhood_i.append(value)
            c_j += 1
        localErrorsWithNeighborhood.append(np.asarray(localErrorsWithNeighborhood_i))
    localErrorsWithNeighborhood = np.asarray(localErrorsWithNeighborhood)
    return localErrorsWithNeighborhood

def slidingWindowApproachForLines(data_structure, distanceToNextSample_2D, distanceToNextSample_50D, slidingWindowSize):
    localErrorsWithSlidingWindow = []
    for i in range(len(data_structure)):
        localErrorsWithSlidingWindow_minMax_i = []
        for j in range(len(data_structure[i]) - 1):
            localDistances_2D_1 = distanceToNextSample_2D[i][max(0, int(j + 1 - slidingWindowSize / 2.0)):max(0, j)]
            localDistances_2D_2 = distanceToNextSample_2D[i][max(0, j + 1):min(int(j + 1 + slidingWindowSize / 2.0),
                                                                               len(data_structure[i]))]
            localDistances_50D_1 = distanceToNextSample_50D[i][max(0, int(j + 1 - slidingWindowSize / 2.0)):max(0, j)]
            localDistances_50D_2 = distanceToNextSample_50D[i][max(0, j + 1):min(int(j + 1 + slidingWindowSize / 2.0),
                                                                                 len(data_structure[i]))]

            currentDistanceError = distanceToNextSample_2D[i][j] - distanceToNextSample_50D[i][j]
            localDistances_2D = np.concatenate([localDistances_2D_1, localDistances_2D_2])
            localDistances_50D = np.concatenate([localDistances_50D_1, localDistances_50D_2])

            localErrors = localDistances_2D - localDistances_50D

            if len(localErrors) == 0:
                value = 0
            else:
                value = (currentDistanceError - statistics.mean(localErrors)) / 2

            localErrorsWithSlidingWindow_minMax_i.append(value)

        localErrorsWithSlidingWindow.append(np.asarray(localErrorsWithSlidingWindow_minMax_i))

    return np.asarray(localErrorsWithSlidingWindow)

def slidingWindowApproachMetricForLines(data_structure, distanceToNextSample_2D, distanceToNextSample_50D,
                                        slidingWindowSize, metric):
    localErrorsWithSlidingWindow = []
    for i in range(len(data_structure)):
        localErrorsWithSlidingWindow_i = []
        for j in range(len(data_structure[i]) - 1):
            subData2D = distanceToNextSample_2D[i][
                        max(0, int(j + 1 - slidingWindowSize / 2.0)):min(int(j + 1 + slidingWindowSize / 2.0),
                                                                         len(data_structure[i]))]
            subData50D = distanceToNextSample_50D[i][
                         max(0, int(j + 1 - slidingWindowSize / 2.0)):min(int(j + 1 + slidingWindowSize / 2.0),
                                                                          len(data_structure[i]))]

            localErrors = metric(subData2D, subData50D)

            localErrorsWithSlidingWindow_i.append(localErrors)

        localErrorsWithSlidingWindow.append(np.asarray(localErrorsWithSlidingWindow_i))

    return np.asarray(localErrorsWithSlidingWindow)
