#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Visualization system to explore multidimensional time series projections.
"""

from collections import OrderedDict
from flask import Flask, render_template, jsonify, request
from natsort import natsorted
import math
import numpy as np
import os
import sklearn as sk
import statistics

import dimRed.debugData as debugData
import dimRed.interpolate as interpolate
import dimRed.intersections as isections
import dimRed.loadData as loadExample
import dimRed.math as ma
import dimRed.metrics as metrics
import dimRed.settings.currentSettings as currentSettings
import dimRed.settings.pathSettings as pathSettings
import dimRed.settingsIO as settingsIO
import dimRed.timeLineMetrics as timeLineMetrics

app = Flask(__name__)

datasets = {}
selectedDataset = ""

data_2D_structure = []
data_50D_structure = []
data_2D_flat = np.empty(0)
data_50D_flat = np.empty(0)

nn_neighbors_2D = np.empty(0)
nn_neighbors_50D = np.empty(0)
pairwise_distances_2D_maxScaled = np.empty(0)
pairwise_distances_50D_maxScaled = np.empty(0)

interpolatedList2D = np.empty(0)
interpolatedList50D = np.empty(0)
data_intersections_50D = []
data_intersections_2D = []
distances50_intersections = []

max_pairwise_50D = 0
distanceToNextSample_2D_maxScale = 0
distanceToNextSample_50D_maxScale = 0

cS = currentSettings.SettingProperties()

@app.route("/")
def main():
    global datasets

    currentPath = os.path.dirname(os.path.abspath(__file__))

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    directories = loadExample.getDatasetPaths(pathSettings.datasetPath)

    trialids = set()
    preprocessingtype = set()
    dimredmethod = set()

    datasetOverview = {}
    for pathSettings.baseDir in directories:
        os.chdir(currentPath)
        os.chdir(os.path.abspath(pathSettings.baseDir))

        # read from file (id, path, settings)
        if not os.path.isfile(pathSettings.visDataPaths):
            print("!! Could not open " + os.path.abspath(pathSettings.visDataPaths))
            continue
        tempDatasetOverview = loadExample.getAllVisTrials(pathSettings.visDataPaths)

        for key, value in tempDatasetOverview.items():
            # preprocessing settings and settings
            tempDatasetOverview[key]["baseDir"] = pathSettings.baseDir
            tempDatasetOverview[key]["settings"] = settingsIO.getSettings(value["settings_path"])
            tempDatasetOverview[key]["preprocessSettings"] = settingsIO.getSettings(value["preprocessSettings_path"])

            trialids.add(tempDatasetOverview[key]["preprocessSettings"]["TrialID"].split("-")[0])
            preprocessingtype.add(tempDatasetOverview[key]["preprocessSettings"]["Preprocessing"])
            dimredmethod.add(tempDatasetOverview[key]["settings"]["DimRed"])

            # file name
            tempDatasetOverview[key]["name"] = os.path.basename(value["2DData_path"])
        datasetOverview.update(tempDatasetOverview)

    datasetOverview["0"] = {"2DData_path": "",
                            "settings_path": "",
                            "preprocessSettings_path": "",
                            "settings": "",
                            "preprocessSettings": "",
                            "highDimData_path": "",
                            "highDimData_type": "",
                            "preprocessedData_path": "",
                            "name": "Select Dataset"}

    datasets = OrderedDict(natsorted(datasetOverview.items()))

    interpolationTypes = {"line": "Straight Line",
                          # "catmullRom": "Catmull Rom",
                          "centripetalCatmullRom": "Centripetal Catmull Rom"}

    sampleMetricTypes = {"equal_sample": "Equal",
                         "time_sample": "Time",
                         "NeighborhoodLoss_sample": "* Local Neighborhood Preservation (q_s2)",
                         "error_50D_n_sample": "* Local Neighborhood Distances: Neighboring Samples in 50D (q_s1)",
                         "error_2D_n_sample": "Distance Differences: Neighboring Samples in 2D",

                         "neighborhood_normalizedStress_sample": "Local Neighborhood: Normalized Stress",
                         "neighborhood_SpearmanCorrelation_sample": "Local Neighborhood: Spearman Correlation",
                         "neighborhood_KendallCorrelation_sample": "Local Neighborhood: Kendall Correlation",
                         "neighborhood_PearsonCorrelation_sample": "Local Neighborhood: Pearson Correlation",
                         "neighborhood_trustworthiness_sample": "Local Neighborhood: Trustworthiness",
                         "neighborhood_continuity_sample": "Local Neighborhood: Continuity",

                         "slidingWindow_normalizedStress_sample": "Sliding Window: Normalized Stress",
                         "slidingWindow_SpearmanCorrelation_sample": "Sliding Window: Spearman Correlation",
                         "slidingWindow_KendallCorrelation_sample": "Sliding Window: Kendall Correlation",
                         "slidingWindow_PearsonCorrelation_sample": "Sliding Window: Pearson Correlation",
                         "slidingWindow_trustworthiness_sample": "Sliding Window: Trustworthiness",
                         "slidingWindow_continuity_sample": "Sliding Window: Continuity",

                         "KruskalStress_sample": "Point-wise Kruskal Stress",
                         "RMSE_sample": "Point-wise RMSE",
                         "error_2D_50D_n_sample": "Point-wise local Error in Neighborhood of Samples (2D and 50D)",
                         }

    lineMetricTypes = {"equal1_line": "Equal (Thick/Color)",
                       "equal2_line": "Equal (Thin/Gray)",
                       "time_line": "Time",
                       "50Ddistance_line": "50D Distance",
                       "2Ddistance_line": "2D Distance",

                       "distanceDifferenceMetric_line": "* Sequential Distances (q_c1)",
                       "slidingWindowDistances_line": "* Sliding Window: Local Distance Variance (q_c2)",
                       "slidingWindow_normalizedStress_line": "Sliding Window: Normalized Stress",
                       }

    trialids = list(trialids)
    trialids.sort()
    preprocessingtype = list(preprocessingtype)
    dimredmethod = list(dimredmethod)

    trialids.insert(0, "All Datasets")
    preprocessingtype.insert(0, "All Preprocessing Types")
    dimredmethod.insert(0, "All Dimensionality Reduction Techniques")

    return render_template("visualizations.html",
                           interpolationTypes=interpolationTypes,
                           trialids=trialids,
                           preprocessingtype=preprocessingtype,
                           dimredmethod=dimredmethod,
                           lineMetricTypes=lineMetricTypes,
                           sampleMetricTypes=sampleMetricTypes)

@app.route("/updateDatasetSelection", methods=["POST"])
def updateDatasetSelection():
    parameters = request.get_json()

    global datasets

    datasetFilter = {}

    for key, value in datasets.items():
        if key != "0":
            if (parameters["trialIds"].startswith("All") or value["preprocessSettings"]["TrialID"].split("-")[0] ==
                str(parameters["trialIds"])) and \
                    (parameters["preprocessingType"].startswith("All") or value["preprocessSettings"][
                        "Preprocessing"] ==
                     parameters["preprocessingType"]) and \
                    (parameters["dimRedMethod"].startswith("All") or value["settings"]["DimRed"] ==
                     parameters["dimRedMethod"]):
                datasetFilter[key] = value

    render_template("visualizations.html", datasets=datasetFilter)

    return jsonify({"datasets": datasetFilter})


@app.route("/data", methods=["POST"])
def data():
    print("Load data...")

    global selectedDataset
    global cS
    global data_2D_structure
    global data_50D_structure
    global data_2D_flat
    global data_50D_flat
    global nn_neighbors_2D
    global nn_neighbors_50D
    global pairwise_distances_2D_maxScaled
    global pairwise_distances_50D_maxScaled
    global max_pairwise_50D  # previous max value...

    parameters = request.get_json()
    samplesList, settings, preprocessingSettings = [], [], []
    sampleListForScreen = []
    data_2D_structure = []
    selectedDataset = None
    data_2D_flat = np.empty(0)
    data_50D_flat = np.empty(0)
    nn_neighbors_2D = np.empty(0)
    nn_neighbors_50D = np.empty(0)
    pairwise_distances_2D_maxScaled = np.empty(0)
    pairwise_distances_50D_maxScaled = np.empty(0)

    selectedDataset = parameters["dataSets"]
    debugData.setDataSet(selectedDataset, cS)

    if selectedDataset is not None and selectedDataset != "0" and selectedDataset in datasets:

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(os.path.abspath(datasets[selectedDataset]["baseDir"]))

        data_2D_structure = []

        # load data set
        samplesList, settings, preprocessingSettings, X_embedded = \
            loadExample.getPreprocessedDataForVis(datasets[selectedDataset]["2DData_path"],
                                                  datasets[selectedDataset]["settings_path"],
                                                  datasets[selectedDataset]["preprocessSettings_path"],
                                                  cS)

        debugData.debugDataSimple(samplesList, "samplesList")

        data_2D_flat = []
        for i in range(len(samplesList)):
            for j in range(len(samplesList[i])):
                coordinates = [samplesList[i][j][0], samplesList[i][j][1]]
                data_2D_flat.append(coordinates)
        data_2D_flat = np.asarray(data_2D_flat)

        debugData.debugDataSimple(data_2D_flat, "--> data_2D_flat")

        # 50D data
        preprocessedDataPath = datasets[selectedDataset]["preprocessedData_path"]
        data_50D_structure, _ = loadExample.getPreprocessedDataForDimRed(preprocessedDataPath, cS)

        # concatenate sublists from list to create nparray
        print(data_50D_flat)
        data_50D_flat = data_50D_structure[0]
        for line in data_50D_structure[1:]:
            data_50D_flat = np.concatenate((data_50D_flat, line), axis=0)

        debugData.debugDataSimple(data_50D_flat, "--> data_50D_flat")

        # determine position on screen
        for i in range(len(samplesList)):
            # scale to range [0, 1]
            dataSamplesForPlot = [[x[0], x[1]] for x in samplesList[i]]
            additionalProperties = [[x[2], x[3]] for x in samplesList[i]]

            data_2D_structure.append(np.array(dataSamplesForPlot))
            sampleListForScreen.append(
                [[d[0], d[1], a[0], a[1]] for d, a in zip(dataSamplesForPlot, additionalProperties)])

        debugData.debugDataSimple(data_2D_structure, "data_2D_structure")
        debugData.debugDataSimple(sampleListForScreen, "samplesList")

        # distances to all neighbors in 2D and 50D
        _, nn_neighbors_2D = ma.sortNearestNeighbors(data_2D_flat)
        _, nn_neighbors_50D = ma.sortNearestNeighbors(data_50D_flat)

        debugData.debugDataSimple(nn_neighbors_2D, "nn_neighbors_2D")
        debugData.debugDataSimple(nn_neighbors_50D, "nn_neighbors_50D")

        pairwise_distances_2D = ma.getPairwiseDistances(data_2D_flat)
        pairwise_distances_50D = ma.getPairwiseDistances(data_50D_flat)

        temp_distances_2D = np.hstack(pairwise_distances_2D)
        temp_distances_50D = np.hstack(pairwise_distances_50D)

        temp_distances_2D = temp_distances_2D / max(temp_distances_2D)
        temp_distances_50D = temp_distances_50D / max(temp_distances_50D)

        debugData.plotScatterplot(np.hstack(temp_distances_2D), np.hstack(temp_distances_50D), "2D", "50D",
                                  "Shepard - Pairwise [0,1]", "PairwiseDistances2D50D-0-1")

        debugData.plotScatterplot(np.hstack(pairwise_distances_2D), np.hstack(pairwise_distances_50D), "2D", "50D",
                                  "Shepard - Pairwise - no scaling", "PairwiseDistances2D50D-noscaling")

        max_pairwise_2D = max(np.hstack(pairwise_distances_2D))
        max_pairwise_50D = max(np.hstack(pairwise_distances_50D))

        pairwise_distances_2D_maxScaled = pairwise_distances_2D / max_pairwise_2D
        pairwise_distances_50D_maxScaled = pairwise_distances_50D / max_pairwise_50D
        debugData.plotScatterplot(np.hstack(pairwise_distances_2D_maxScaled),
                                  np.hstack(pairwise_distances_50D_maxScaled),
                                  "2D", "50D", "Shepard - Pairwise - no scaling", "PairwiseDistances2D50D-noscaling",
                                  False, max_pairwise_2D, max_pairwise_50D)

        debugData.debugDataSimple(pairwise_distances_2D_maxScaled, "pairwise_distances_2D_maxScaled")
        debugData.debugDataSimple(pairwise_distances_50D_maxScaled, "pairwise_distances_50D_maxScaled")

        numSamples = data_2D_flat.shape[0]  # #samples
        numDims = data_50D_flat.shape[1]  # #dimensions

        debugData.debugDataSimple(numSamples, "numSamples")
        debugData.debugDataSimple(numDims, "numDims")

    return jsonify({"samples": sampleListForScreen,
                    "settings": settings,
                    "preprocessingSettings": preprocessingSettings,
                    "name": datasets[selectedDataset]["name"] if selectedDataset in datasets else ""})

@app.route("/overallMetrics", methods=["POST"])
def overallMetrics():
    global distanceToNextSample_2D_maxScale
    global distanceToNextSample_50D_maxScale
    global nn_neighbors_2D
    global nn_neighbors_50D

    parameters = request.get_json()
    localNeighborhoodSize = parameters["localNeighborhoodSize"]

    metricValues = {}
    metricStrings = {}

    metricValues["trustworthiness"] = metrics.trustworthiness(nn_neighbors_2D, nn_neighbors_50D,
                                                              localNeighborhoodSize)
    metricValues["continuity"] = metrics.continuity(nn_neighbors_2D, nn_neighbors_50D, localNeighborhoodSize)

    metricValues["normalizedStress"] = metrics.normalizedStress(pairwise_distances_2D_maxScaled,
                                                                pairwise_distances_50D_maxScaled)

    metricValues["normalizedStress_time"] = metrics.normalizedStress(distanceToNextSample_2D_maxScale,
                                                                     distanceToNextSample_50D_maxScale)

    metricValues["pearson"] = metrics.pearsonCorrelation(pairwise_distances_2D_maxScaled,
                                                         pairwise_distances_50D_maxScaled)
    metricValues["spearman"] = metrics.spearmanCorrelation(pairwise_distances_2D_maxScaled,
                                                           pairwise_distances_50D_maxScaled)
    metricValues["kendall"] = metrics.kendallCorrelation(pairwise_distances_2D_maxScaled,
                                                         pairwise_distances_50D_maxScaled)

    metricValues["pearson_time"] = metrics.pearsonCorrelation(distanceToNextSample_2D_maxScale,
                                                              distanceToNextSample_50D_maxScale)
    metricValues["spearman_time"] = metrics.spearmanCorrelation(distanceToNextSample_2D_maxScale,
                                                                distanceToNextSample_50D_maxScale)
    metricValues["kendall_time"] = metrics.kendallCorrelation(distanceToNextSample_2D_maxScale,
                                                              distanceToNextSample_50D_maxScale)

    # to strings
    metricStrings["trustworthiness"] = "{0:.4f}".format(metricValues["trustworthiness"])
    metricStrings["continuity"] = "{0:.4f}".format(metricValues["continuity"])
    metricStrings["normalizedStress"] = "{0:.4f}".format(metricValues["normalizedStress"])
    metricStrings["normalizedStress_time"] = "{0:.4f}".format(metricValues["normalizedStress_time"])

    metricStrings["pearson"] = "{0:.4f}".format(metricValues["pearson"])
    metricStrings["spearman"] = "{0:.4f}".format(metricValues["spearman"])
    metricStrings["kendall"] = "{0:.4f}".format(metricValues["kendall"])

    metricStrings["pearson_time"] = "{0:.4f}".format(metricValues["pearson_time"])
    metricStrings["spearman_time"] = "{0:.4f}".format(metricValues["spearman_time"])
    metricStrings["kendall_time"] = "{0:.4f}".format(metricValues["kendall_time"])

    return jsonify({"metrics": metricStrings})

@app.route("/lines", methods=["POST"])
def lines():
    parameters = request.get_json()
    sampleCount = parameters["subsampleCount"]
    interpolationType = parameters["interpolationType"]

    global data_2D_structure
    global interpolatedList2D
    global data_50D_structure
    global interpolatedList50D
    interpolatedList2D = []

    for dataSamples in data_2D_structure:
        interpolated = np.array([])
        if interpolationType == "line":
            interpolated = [[x] for x in dataSamples.tolist()]
        elif interpolationType == "catmullRom":
            interpolated = interpolate.CatmullRomChain(np.array(dataSamples)[:, :2], sampleCount)
        elif interpolationType == "centripetalCatmullRom":
            interpolated = interpolate.CentripetalCatmullRomChain(np.array(dataSamples)[:, :2], sampleCount)
        interpolatedList2D.append(interpolated)

    if interpolationType == "no":
        return jsonify({"interpolated": []})

    # high dim interpolation
    interpolatedList50D = []
    for dataSamples in data_50D_structure:
        interpolated50D = np.array([])
        if interpolationType == "line":
            interpolated50D = [[x] for x in dataSamples.tolist()]
        elif interpolationType == "catmullRom":
            interpolated50D = interpolate.CatmullRomChain(np.array(dataSamples)[:, :], sampleCount)
        elif interpolationType == "centripetalCatmullRom":
            interpolated50D = interpolate.CentripetalCatmullRomChain(np.array(dataSamples)[:, :], sampleCount)
        interpolatedList50D.append(interpolated50D)

    return jsonify({"interpolated": interpolatedList2D})

@app.route("/intersections", methods=["POST"])
def intersections():
    global data_intersections_2D
    global data_intersections_50D
    global distances50_intersections
    global interpolatedList50D

    timeLineLengths = []
    connectionLengths = []
    d = []
    for a in interpolatedList2D:
        timeLineLengths.append(len(a))
        for b in a:
            connectionLengths.append(len(b))
            for c in b:
                d.append(np.asarray(c))

    iSections = isections.getIntersections(np.asarray(d), timeLineLengths, connectionLengths[0])  # 2D projections

    distances50_intersections = []
    data_intersections_2D = np.asarray([[x["x"], x["y"]] for x in iSections])

    for intersection in iSections:
        startSegment2D_1 = np.asarray(interpolatedList2D[intersection["ts1"]][intersection["seg1"]][intersection["p1"]])
        nextSegment = len(interpolatedList2D[intersection["ts1"]][intersection["seg1"]]) >= intersection["p1"] + 1
        endSegment2D_1 = np.asarray(interpolatedList2D[intersection["ts1"]][intersection["seg1"] + 1 if nextSegment else
            intersection["seg1"]][0 if nextSegment else intersection["p1"] + 1])

        startSegment2D_2 = np.asarray(interpolatedList2D[intersection["ts2"]][intersection["seg2"]][intersection["p2"]])
        nextSegment = len(interpolatedList2D[intersection["ts2"]][intersection["seg2"]]) >= intersection["p2"] + 1
        endSegment2D_2 = np.asarray(interpolatedList2D[intersection["ts2"]][intersection["seg2"] + 1 if nextSegment else
            intersection["seg2"]][0 if nextSegment else intersection["p2"] + 1])

        point = np.asarray([intersection["x"], intersection["y"]])
        lineLength_1 = math.sqrt(sum((endSegment2D_1 - startSegment2D_1) ** 2))
        lineLength_2 = math.sqrt(sum((endSegment2D_2 - startSegment2D_2) ** 2))
        linePartLength_1 = math.sqrt(sum((point - startSegment2D_1) ** 2))
        linePartLength_2 = math.sqrt(sum((point - startSegment2D_2) ** 2))

        ratio_1 = linePartLength_1 / lineLength_1
        ratio_2 = linePartLength_2 / lineLength_2

        startSegment50D_1 = np.asarray(
            interpolatedList50D[intersection["ts1"]][intersection["seg1"]][intersection["p1"]])
        nextSegment = len(interpolatedList2D[intersection["ts1"]][intersection["seg1"]]) >= intersection["p1"] + 1
        endSegment50D_1 = np.asarray(
            interpolatedList50D[intersection["ts1"]][intersection["seg1"] + 1 if nextSegment else
            intersection["seg1"]][0 if nextSegment else intersection["p1"] + 1])

        startSegment50D_2 = np.asarray(
            interpolatedList50D[intersection["ts2"]][intersection["seg2"]][intersection["p2"]])
        nextSegment = len(interpolatedList2D[intersection["ts2"]][intersection["seg2"]]) >= intersection["p2"] + 1
        endSegment50D_2 = np.asarray(
            interpolatedList50D[intersection["ts2"]][intersection["seg2"] + 1 if nextSegment else
            intersection["seg2"]][0 if nextSegment else intersection["p2"] + 1])

        intersection50D_1 = startSegment50D_1 + (endSegment50D_1 - startSegment50D_1) * ratio_1
        intersection50D_2 = startSegment50D_2 + (endSegment50D_2 - startSegment50D_2) * ratio_2

        distanceIntersection50D = math.sqrt(sum((intersection50D_1 - intersection50D_2) ** 2))

        epsilon = 0.00001  # as we are dealing with float here
        min_scaledPairwise_50D = min(np.hstack(pairwise_distances_50D_maxScaled))
        distances50_intersections.append(
            distanceIntersection50D if distanceIntersection50D > min_scaledPairwise_50D + epsilon else 0)  # TODO reasonable?

    return jsonify({"halos": iSections})

@app.route("/newMetrics", methods=["POST"])
def newMetrics():
    parameters = request.get_json()

    sampleColorMetricId = parameters["sampleMetricId"]
    sampleWidthMetricId = parameters["sampleMetricId"]
    lineColorMetricId = parameters["lineMetricId"]
    lineThicknessMetricId = parameters["lineMetricId"]
    slidingWindowSize = parameters["slidingWindowSize"]
    maxNumberOfNeighbors = parameters["maxNumberOfNeighbors"]

    maxScaling_samples = parameters["maxScaling_samples"]
    minMaxScaling_samples = parameters["minMaxScaling_samples"]
    posNegScaling_samples = parameters["posNegScaling_samples"]
    standardization_samples = parameters["standardization_samples"]
    maxScaling_connections = parameters["maxScaling_connections"]
    minMaxScaling_connections = parameters["minMaxScaling_connections"]
    posNegScaling_connections = parameters["posNegScaling_connections"]
    standardization_connections = parameters["standardization_connections"]

    global data_2D_structure
    global data_2D_flat
    global data_50D_flat
    global nn_neighbors_2D
    global nn_neighbors_50D
    global pairwise_distances_2D_maxScaled
    global pairwise_distances_50D_maxScaled
    global distances50_intersections

    global distanceToNextSample_2D_maxScale
    global distanceToNextSample_50D_maxScale
    global nn_neighbors_2D
    global nn_neighbors_50D

    global max_pairwise_50D  # previous max value...

    sampleMetricValues = {}
    lineMetricValues = {}

    # temporal position - [0,1]
    # color points/lines depending on (temporal) position in sequence
    if "time_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        timePositionOfSamples = timeLineMetrics.temporalPosition(data_2D_structure, "samples")
        debugData.debugData(timePositionOfSamples, "timePositionOfSamples")
        sampleMetricValues["time_sample"] = timePositionOfSamples
    if "time_line" in [lineColorMetricId, lineThicknessMetricId]:
        timePositionOfLines = timeLineMetrics.temporalPosition(data_2D_structure, "lines")
        debugData.debugData(timePositionOfLines, "timePositionOfLines")
        lineMetricValues["time_line"] = timePositionOfLines

    # equal values - [0,1]
    # e.g., color points/lines with same color, use same size
    if "equal_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        equalSamples = timeLineMetrics.equalValues(data_2D_structure, 0.5, "samples")
        debugData.debugData(equalSamples, "equalSamples")
        sampleMetricValues["equal_sample"] = equalSamples
    if "equal1_line" in [lineColorMetricId, lineThicknessMetricId]:
        equalLines = timeLineMetrics.equalValues(data_2D_structure, 0.35, "lines")
        debugData.debugData(equalLines, "equalLines")
        lineMetricValues["equal1_line"] = equalLines
    if "equal2_line" in [lineColorMetricId, lineThicknessMetricId]:
        equalLines2 = timeLineMetrics.equalValues(data_2D_structure, 0, "lines")
        debugData.debugData(equalLines2, "equalLines2")
        lineMetricValues["equal2_line"] = equalLines2

    # distances to next sampe
    distanceToNextSample_2D, distanceToNextSample_50D = \
        ma.getDistancesToNextSample(data_2D_structure, pairwise_distances_2D_maxScaled,
                                    pairwise_distances_50D_maxScaled)

    # stretch lists to [?,1]; distance 0 in 2D should be 0 in 50D, max distances should be mas distances
    maxDistance2D_toNextSample = np.max(np.hstack(distanceToNextSample_2D))
    maxDistance50D_toNextSample = np.max(np.hstack(distanceToNextSample_50D))
    meanDistance50D = np.mean(np.hstack(distanceToNextSample_50D))
    stdDistance50D = np.std(np.hstack(distanceToNextSample_50D))

    distanceToNextSample_2D_maxScale = distanceToNextSample_2D / maxDistance2D_toNextSample
    distanceToNextSample_50D_maxScale = distanceToNextSample_50D / maxDistance50D_toNextSample
    debugData.debugData(distanceToNextSample_2D_maxScale, "distanceToNextSample_2D_maxScale")
    debugData.debugData(distanceToNextSample_50D_maxScale, "distanceToNextSample_50D_maxScale")

    lineMetricValues["50Ddistance_line"] = distanceToNextSample_50D_maxScale
    lineMetricValues["2Ddistance_line"] = distanceToNextSample_2D_maxScale

    # distance difference
    if "distanceDifferenceMetric_line" in [lineColorMetricId, lineThicknessMetricId]:
        distanceDiff = ma.getDistanceDifferences(distanceToNextSample_50D_maxScale,
                                                 distanceToNextSample_2D_maxScale)
        debugData.debugData(distanceDiff, "distanceDiff")
        lineMetricValues["distanceDifferenceMetric_line"] = distanceDiff

    # local neighborhood for samples
    if "neighborhood_normalizedStress_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_normalizedStress_sample = \
            timeLineMetrics.localNeighborhoodApproachMetricForSamples(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                      pairwise_distances_50D_maxScaled, nn_neighbors_50D,
                                                                      maxNumberOfNeighbors, metrics.normalizedStress)
        debugData.debugData(neighborhood_normalizedStress_sample,
                            "neighborhood_normalizedStress_sample")
        sampleMetricValues[
            "neighborhood_normalizedStress_sample"] = neighborhood_normalizedStress_sample

    if "neighborhood_SpearmanCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_SpearmanCorrelation_sample = \
            timeLineMetrics.localNeighborhoodApproachMetricForSamples(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                      pairwise_distances_50D_maxScaled, nn_neighbors_50D,
                                                                      maxNumberOfNeighbors, metrics.spearmanCorrelation)
        debugData.debugData(neighborhood_SpearmanCorrelation_sample,
                            "neighborhood_SpearmanCorrelation_sample")
        sampleMetricValues[
            "neighborhood_SpearmanCorrelation_sample"] = neighborhood_SpearmanCorrelation_sample

    if "neighborhood_KendallCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_KendallCorrelation_sample = \
            timeLineMetrics.localNeighborhoodApproachMetricForSamples(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                      pairwise_distances_50D_maxScaled, nn_neighbors_50D,
                                                                      maxNumberOfNeighbors, metrics.kendallCorrelation)
        debugData.debugData(neighborhood_KendallCorrelation_sample,
                            "neighborhood_KendallCorrelation_sample")
        sampleMetricValues[
            "neighborhood_KendallCorrelation_sample"] = neighborhood_KendallCorrelation_sample

    if "neighborhood_PearsonCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_PearsonCorrelation_sample = \
            timeLineMetrics.localNeighborhoodApproachMetricForSamples(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                      pairwise_distances_50D_maxScaled, nn_neighbors_50D,
                                                                      maxNumberOfNeighbors, metrics.pearsonCorrelation)
        debugData.debugData(neighborhood_PearsonCorrelation_sample,
                            "neighborhood_PearsonCorrelation_sample")
        sampleMetricValues[
            "neighborhood_PearsonCorrelation_sample"] = neighborhood_PearsonCorrelation_sample

    # my distance approach
    if "error_2D_n_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        localErrorsWithNeighborhood2D = \
            timeLineMetrics.localNeighborhoodApproachForSamples_2D(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                   pairwise_distances_50D_maxScaled, maxNumberOfNeighbors,
                                                                   nn_neighbors_2D)
        debugData.debugData(localErrorsWithNeighborhood2D, "localErrorsWithNeighborhood2D")
        sampleMetricValues["error_2D_n_sample"] = localErrorsWithNeighborhood2D

    if "error_50D_n_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        localErrorsWithNeighborhood50D = \
            timeLineMetrics.localNeighborhoodApproachForSamples_50D(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                    pairwise_distances_50D_maxScaled, maxNumberOfNeighbors,
                                                                    nn_neighbors_50D)
        debugData.debugData(localErrorsWithNeighborhood50D, "localErrorsWithNeighborhood50D")
        sampleMetricValues["error_50D_n_sample"] = localErrorsWithNeighborhood50D

    if "error_2D_50D_n_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        localErrorsWithNeighborhoodCombined = \
            timeLineMetrics.localNeighborhoodApproachForSamples_Combined(data_2D_structure, pairwise_distances_2D_maxScaled,
                                                                         pairwise_distances_50D_maxScaled,
                                                                         maxNumberOfNeighbors,
                                                                         nn_neighbors_2D, nn_neighbors_50D)
        debugData.debugData(localErrorsWithNeighborhoodCombined, "localErrorsWithNeighborhoodCombined")
        sampleMetricValues["error_2D_50D_n_sample"] = localErrorsWithNeighborhoodCombined

    # slidingWindow for samples
    if "slidingWindow_normalizedStress_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_normalizedStress_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples(data_2D_structure, distanceToNextSample_2D_maxScale,
                                                                  distanceToNextSample_50D_maxScale, slidingWindowSize,
                                                                  metrics.normalizedStress)
        debugData.debugData(slidingWindow_normalizedStress_sample, "slidingWindow_normalizedStress_sample")
        sampleMetricValues["slidingWindow_normalizedStress_sample"] = slidingWindow_normalizedStress_sample

    if "slidingWindow_SpearmanCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_SpearmanCorrelation_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples(data_2D_structure, distanceToNextSample_2D_maxScale,
                                                                  distanceToNextSample_50D_maxScale, slidingWindowSize,
                                                                  metrics.spearmanCorrelation)
        debugData.debugData(slidingWindow_SpearmanCorrelation_sample,
                            "slidingWindow_SpearmanCorrelation_sample")
        sampleMetricValues[
            "slidingWindow_SpearmanCorrelation_sample"] = slidingWindow_SpearmanCorrelation_sample

    if "slidingWindow_KendallCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_KendallCorrelation_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples(data_2D_structure, distanceToNextSample_2D_maxScale,
                                                                  distanceToNextSample_50D_maxScale, slidingWindowSize,
                                                                  metrics.kendallCorrelation)
        debugData.debugData(slidingWindow_KendallCorrelation_sample,
                            "slidingWindow_KendallCorrelation_sample")
        sampleMetricValues[
            "slidingWindow_KendallCorrelation_sample"] = slidingWindow_KendallCorrelation_sample

    if "slidingWindow_PearsonCorrelation_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_PearsonCorrelation_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples(data_2D_structure, distanceToNextSample_2D_maxScale,
                                                                  distanceToNextSample_50D_maxScale, slidingWindowSize,
                                                                  metrics.pearsonCorrelation)
        debugData.debugData(slidingWindow_PearsonCorrelation_sample,
                            "slidingWindow_PearsonCorrelation_sample")
        sampleMetricValues[
            "slidingWindow_PearsonCorrelation_sample"] = slidingWindow_PearsonCorrelation_sample

    if "slidingWindow_trustworthiness_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_Trustworthiness_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples2(nn_neighbors_2D, nn_neighbors_50D, slidingWindowSize,
                                                                   metrics.trustworthiness, True)
        sampleMetricValues[
            "slidingWindow_trustworthiness_sample"] = slidingWindow_Trustworthiness_sample

    if "slidingWindow_continuity_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        slidingWindow_Continuity_sample = \
            timeLineMetrics.slidingWindowApproachMetricForSamples2(nn_neighbors_2D, nn_neighbors_50D, slidingWindowSize,
                                                                   metrics.continuity, True)
        sampleMetricValues[
            "slidingWindow_continuity_sample"] = slidingWindow_Continuity_sample

    if "neighborhood_trustworthiness_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_Trustworthiness_sample =\
            timeLineMetrics.localNeighborhoodApproachMetricForSamples2(nn_neighbors_2D, nn_neighbors_50D,
                                                                       maxNumberOfNeighbors, metrics.trustworthiness, True)
        sampleMetricValues[
            "neighborhood_trustworthiness_sample"] = neighborhood_Trustworthiness_sample

    if "neighborhood_continuity_sample" in [sampleColorMetricId, sampleWidthMetricId]:
        neighborhood_Continuity_sample = timeLineMetrics.localNeighborhoodApproachMetricForSamples2(nn_neighbors_2D,
                                                                                                    nn_neighbors_50D,
                                                                                                    maxNumberOfNeighbors,
                                                                                                    metrics.continuity,
                                                                                                    True)
        sampleMetricValues[
            "neighborhood_continuity_sample"] = neighborhood_Continuity_sample

    # sliding window
    if "slidingWindowDistances_line" in [lineColorMetricId, lineThicknessMetricId]:
        localErrorsWithSlidingWindow = \
            timeLineMetrics.slidingWindowApproachForLines(data_2D_structure, distanceToNextSample_2D_maxScale,
                                                          distanceToNextSample_50D_maxScale, slidingWindowSize)
        debugData.debugData(localErrorsWithSlidingWindow, "localErrorsWithSlidingWindow")
        lineMetricValues["slidingWindowDistances_line"] = localErrorsWithSlidingWindow

    if "slidingWindow_normalizedStress_line" in [lineColorMetricId, lineThicknessMetricId]:
        lineMetricValues["slidingWindow_normalizedStress_line"] = timeLineMetrics.slidingWindowApproachMetricForLines(
            data_2D_structure, distanceToNextSample_2D_maxScale, distanceToNextSample_50D_maxScale,
            slidingWindowSize, metrics.normalizedStress)

    if any(x in ["RMSE_sample", "KruskalStress_sample", "NeighborhoodLoss_sample"] for x in [sampleColorMetricId, sampleWidthMetricId]):
        # metrics for samples
        rmse = metrics.RMSEForAllSamples(pairwise_distances_2D_maxScaled, pairwise_distances_50D_maxScaled)
        kruskalStress = metrics.kruskalStressForAllSamples(pairwise_distances_2D_maxScaled,
                                                           pairwise_distances_50D_maxScaled)
        neighborhoodLoss = metrics.neighborhoodLossForAllSamplse(nn_neighbors_2D, nn_neighbors_50D,
                                                                 maxNumberOfNeighbors)

        # bring in correct shape
        sampleMetricValues["RMSE_sample"] = []
        sampleMetricValues["KruskalStress_sample"] = []
        sampleMetricValues["NeighborhoodLoss_sample"] = []

        c = 0
        for i in range(len(data_2D_structure)):
            rmse_j = []
            kruskalStress_j = []
            neighborhoodLoss_j = []
            for j in range(len(data_2D_structure[i])):
                rmse_j.append(rmse[c])
                kruskalStress_j.append(kruskalStress[c])
                neighborhoodLoss_j.append(neighborhoodLoss[c])
                c += 1
            sampleMetricValues["RMSE_sample"].append(np.asarray(rmse_j))
            sampleMetricValues["KruskalStress_sample"].append(np.asarray(kruskalStress_j))
            sampleMetricValues["NeighborhoodLoss_sample"].append(np.asarray(neighborhoodLoss_j))

        sampleMetricValues["RMSE_sample"] = np.asarray(sampleMetricValues["RMSE_sample"])
        sampleMetricValues["KruskalStress_sample"] = np.asarray(sampleMetricValues["KruskalStress_sample"])
        sampleMetricValues["NeighborhoodLoss_sample"] = np.asarray(sampleMetricValues["NeighborhoodLoss_sample"])

    meanDistance2D = np.mean(np.hstack(distanceToNextSample_2D))
    stdDistance2D = np.std(np.hstack(distanceToNextSample_2D))

    # intersections
    distances50_intersections_maxScaledNeighboringSamples = \
        (np.asarray(distances50_intersections) / maxDistance50D_toNextSample / max_pairwise_50D).tolist()

    # final metrics
    sampleColorMetric = sampleMetricValues[sampleColorMetricId]
    sampleWidthMetric = sampleMetricValues[sampleWidthMetricId]
    lineColorMetric = lineMetricValues[lineColorMetricId]
    lineThicknessMetric = lineMetricValues[lineThicknessMetricId]

    # if expscale:
    #    sampleColorMetric = np.sign(sampleColorMetric) * np.exp(np.abs(sampleColorMetric))
    #    sampleWidthMetric = np.sign(sampleWidthMetric) * np.exp(np.abs(sampleWidthMetric))
    #    lineColorMetric = np.sign(lineColorMetric) * np.exp(np.abs(lineColorMetric))
    #    lineThicknessMetric = np.sign(lineThicknessMetric) * np.exp(np.abs(lineThicknessMetric))
    # elif squarescale:
    #    sampleColorMetric = np.sign(sampleColorMetric) * np.square(np.abs(sampleColorMetric))
    #    sampleWidthMetric = np.sign(sampleWidthMetric) * np.square(np.abs(sampleWidthMetric))
    #    lineColorMetric = np.sign(lineColorMetric) * np.square(np.abs(lineColorMetric))
    #    lineThicknessMetric = np.sign(lineThicknessMetric) * np.square(np.abs(lineThicknessMetric))
    # elif sqrtscale:
    #    sampleColorMetric = np.sign(sampleColorMetric) * np.sqrt(np.abs(sampleColorMetric))
    #    sampleWidthMetric = np.sign(sampleWidthMetric) * np.sqrt(np.abs(sampleWidthMetric))
    #    lineColorMetric = np.sign(lineColorMetric) * np.sqrt(np.abs(lineColorMetric))
    #    lineThicknessMetric = np.sign(lineThicknessMetric) * np.sqrt(np.abs(lineThicknessMetric))
    # if reverse:
    #    sampleColorMetric = -1 * sampleColorMetric
    #    sampleWidthMetric = -1 * sampleWidthMetric
    #    lineColorMetric = -1 * lineColorMetric
    #    lineThicknessMetric = -1 * lineThicknessMetric

    if standardization_samples:  # median is at 0...

        if sampleColorMetricId != "NeighborhoodLoss_sample":
            temp = sk.preprocessing.scale(np.hstack(sampleColorMetric))
            metricValues = []
            c = 0
            for i in range(len(data_2D_structure)):
                m = []
                for j in range(len(data_2D_structure[i])):
                    m.append(temp[c])
                    c += 1
                metricValues.append(np.asarray(m))
            sampleColorMetric = np.asarray(metricValues)

        if sampleWidthMetricId != "NeighborhoodLoss_sample":
            temp = sk.preprocessing.scale(np.hstack(sampleWidthMetric))
            metricValues = []
            c = 0
            for i in range(len(data_2D_structure)):
                m = []
                for j in range(len(data_2D_structure[i])):
                    m.append(temp[c])
                    c += 1
                metricValues.append(np.asarray(m))
            sampleWidthMetric = np.asarray(metricValues)

        if np.absolute(ma.getMax(sampleColorMetric)) > 0 or np.absolute(
                ma.getMin(sampleColorMetric)) > 0:
            sampleColorMetric = sampleColorMetric / max(np.absolute(ma.getMax(sampleColorMetric)),
                                                        np.absolute(ma.getMin(sampleColorMetric)))
        if np.absolute(ma.getMax(sampleWidthMetric)) > 0 or np.absolute(
                ma.getMin(sampleWidthMetric)) > 0:
            sampleWidthMetric = sampleWidthMetric / max(np.absolute(ma.getMax(sampleWidthMetric)),
                                                        np.absolute(ma.getMin(sampleWidthMetric)))

    elif posNegScaling_samples:
        sampleColorMetric = ma.minMaxScale(sampleColorMetric, 0, 2) - 1
        sampleWidthMetric = ma.minMaxScale(sampleWidthMetric, 0, 2) - 1
    elif minMaxScaling_samples:
        sampleColorMetric = ma.minMaxScale(sampleColorMetric, 0, 1)
        sampleWidthMetric = ma.minMaxScale(sampleWidthMetric, 0, 1)

    elif maxScaling_samples:
        sampleColorMetric = sampleColorMetric / np.max(np.abs(sampleColorMetric))
        sampleWidthMetric = sampleWidthMetric / np.max(np.abs(sampleWidthMetric))

    if standardization_connections:  # median is at 0...
        temp = sk.preprocessing.scale(np.hstack(lineColorMetric))
        metricValues = []
        c = 0
        for i in range(len(data_2D_structure)):
            m = []
            for j in range(len(data_2D_structure[i]) - 1):
                m.append(temp[c])
                c += 1
            metricValues.append(np.asarray(m))
        lineColorMetric = np.asarray(metricValues)

        temp = sk.preprocessing.scale(np.hstack(lineThicknessMetric))
        metricValues = []
        c = 0
        for i in range(len(data_2D_structure)):
            m = []
            for j in range(len(data_2D_structure[i]) - 1):
                m.append(temp[c])
                c += 1
            metricValues.append(np.asarray(m))
        lineThicknessMetric = np.asarray(metricValues)

        if np.absolute(ma.getMax(lineColorMetric)) > 0 or np.absolute(
                ma.getMin(lineColorMetric)) > 0:
            lineColorMetric = lineColorMetric / max(np.absolute(ma.getMax(lineColorMetric)),
                                                    np.absolute(ma.getMin(lineColorMetric)))
        if np.absolute(ma.getMax(lineThicknessMetric)) > 0 or np.absolute(
                ma.getMin(lineThicknessMetric)) > 0:
            lineThicknessMetric = lineThicknessMetric / max(np.absolute(ma.getMax(lineThicknessMetric)),
                                                            np.absolute(ma.getMin(lineThicknessMetric)))
    elif posNegScaling_connections:
        lineColorMetric = ma.minMaxScale(lineColorMetric, 0, 2) - 1
        lineThicknessMetric = ma.minMaxScale(lineThicknessMetric, 0, 2) - 1
    elif minMaxScaling_connections:
        lineColorMetric = ma.minMaxScale(lineColorMetric, 0, 1)
        lineThicknessMetric = ma.minMaxScale(lineThicknessMetric, 0, 1)

    elif maxScaling_connections:
        lineColorMetric = lineColorMetric / np.max(np.abs(lineColorMetric))
        lineThicknessMetric = lineThicknessMetric / np.max(np.abs(lineThicknessMetric))

    sampleColorMetric = [x.tolist() for x in sampleColorMetric]
    sampleWidthMetric = [x.tolist() for x in sampleWidthMetric]
    lineColorMetric = [x.tolist() for x in lineColorMetric]
    lineThicknessMetric = [x.tolist() for x in lineThicknessMetric]

    result = {"sampleColorMetric": sampleColorMetric,
              "sampleWidthMetric": sampleWidthMetric,
              "lineColorMetric": lineColorMetric,
              "lineThicknessMetric": lineThicknessMetric,
              "distances2D": np.hstack(distanceToNextSample_2D_maxScale).tolist(),
              "distances50D": np.hstack(distanceToNextSample_50D_maxScale).tolist(),
              "haloMetric": distances50_intersections_maxScaledNeighboringSamples,
              "maxDistance50D": 1,
              "meanDistance50D": meanDistance50D / maxDistance50D_toNextSample,
              "meanDistance2D": meanDistance2D / maxDistance2D_toNextSample,
              "stdDistance50D": stdDistance50D / maxDistance2D_toNextSample,
              "stdDistance2D": stdDistance2D / maxDistance2D_toNextSample,
              "meanSampleWidthMetric": statistics.mean([x for sub in sampleWidthMetric for x in sub]),
              "meanSampleColorMetric": statistics.mean([x for sub in sampleColorMetric for x in sub]),
              "meanLineColorMetric": statistics.mean([x for sub in lineColorMetric for x in sub]),
              "meanLineThicknessMetric": statistics.mean([x for sub in lineThicknessMetric for x in sub])
              }

    return jsonify(result)
