#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Generates high dimensional data from different input types.
"""

from PIL import Image
from collections import defaultdict
from natsort import natsorted
from os import listdir
from os.path import isfile, join
import csv
import numpy as np
import os
import pandas as pd
import re

"""
Generates high dimensional data from video frames/images.
Supports just one data set.
"""
def getDataFromImages(files):
    m = []
    labels = []
    width = 0
    height = 0

    print("Extract high dimensional data...")

    for fileName in files:
        row = []
        # filename
        im = Image.open(fileName)
        pix = im.load()

        # rgb values
        for y in range(im.height):
            for x in range(im.width):
                row.append(pix[x, y][0])
                row.append(pix[x, y][1])
                row.append(pix[x, y][2])

        m.append(row)

        width = im.width
        height = im.height
        im.close()

        # for label
        labels.append(int([float(s) for s in re.findall(r'-?\d+\.?\d*', fileName)][-1]))

    print("...data collected")
    return np.array(m), labels, width, height

"""
Generates high dimensional data from common csv files where every line represents one sample.
"""
def getDataForCSVFiles(files, cS):

    print(files)

    dataLengths = []
    m = np.array([])
    labels = np.array([])

    for file in files:
        df = pd.DataFrame()

        # pandas load chunks
        for x in pd.read_csv(file, header=None, chunksize=2):
            df = pd.concat([df, x], ignore_index=True)
        #df = pd.read_csv(file, sep=',', header=None)

        if m.size == 0:
            m = df.values
            labels = np.arange(len(m))
        else:
            m = np.concatenate((m, df.values))
            labels = np.concatenate((labels, np.arange(len(m))))
        dataLengths.append(len(df.values))

    if cS.ignoreFirstDimension:
        m = np.delete(m, 0, 1)
    return m, labels, dataLengths

def getDataForCSVFile(file, cS):
    m = []
    labels = []
    with open(file, "r") as csvfile:
        datareader = csv.reader(csvfile)
        currentM = []
        for row in datareader:
            if row:
                currentM.append(row)
            else:
                if cS.ignoreFirstDimension:
                    currentM = np.delete(currentM, 0, 1)
                m.append(np.array(currentM).astype(float))
                labels.append([x for x in range(len(currentM))])
                currentM = []
    if currentM:
        if cS.ignoreFirstDimension:
            currentM = np.delete(currentM, 0, 1)
        m.append(np.array(currentM).astype(float))
        labels.append([x for x in range(len(currentM))])

    return m, labels

"""
Generates high dimensional data from many csv files where one csv file represents one sample.
Supports just one data set.
"""
def getDataForManyCSVFiles(directories):
    for directory in directories:  # uses just the first dataset
        fileNames = natsorted([f for f in listdir(directory) if isfile(join(directory, f))])
        fileNames = [fileName for fileName in fileNames if fileName.endswith("csv")]
        startLabel = -1

        m = []
        labels = []

        for current_id, fileName in enumerate(fileNames):
            currentTime = fileName[5:]
            if startLabel == -1:
                startLabel = currentTime

            # file to matrix
            with open(os.path.join(directory, fileName), 'rt') as csvfile:
                r = []
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')

                for i, row in enumerate(fileReader):
                    if i == 0:
                        continue
                    ex = [float(x) for x in row]
                    r.extend(ex)

                m.append(r)
            labels.append(current_id)

        return np.array(m), labels

"""
Generates high dimensional data from a bgraph.
Supports just one data set.
"""
def getDataForBgraph(file):
    labels = []
    m = []
    # read the file
    with open(file, 'r') as f:
        edges = []
        graphs = []

        lineCount = 0
        lines = f.readlines()
        while lines[lineCount] == "":
            lineCount += 1
            continue

        # -- old format --
        # starts with "arbitrary graph;"
        if lines[lineCount] == "arbitrary graph;":
            print("BGRAPH_1")
            graphID = -1
            graph = defaultdict(lambda: 0)

            while lineCount <= len(lines):
                line = lines[lineCount]

                # ignore empty lines
                if line == "":
                    continue

                # delete semicolon at the end of the line
                if line[-1] == ";":
                    line = line[:-1]

                # split in single sections of the line
                stringList = line.split(' ')

                if len(stringList) >= 2:
                    # start of a new graph:
                    # name of the graph consists of two words
                    graphTitle = stringList[0] + " " + stringList[1]
                    graphID += 1
                    labels.append(graphTitle)

                    # go over each section of the line
                    for i in range(int(len(stringList) / 3)):  # 2 to len(stringList) - 1; every 3
                        # each edge consists of 3 parts:
                        # start node, destination node, weight
                        if 2 + i * 3 + 3 < len(stringList):
                            start = stringList[2 + i * 3]
                            end = stringList[2 + i * 3 + 1]
                            weight = float(stringList[2 + i * 3 + 2])

                            if start not in edges:
                                edges.append(start)
                            start = edges.index(start)
                            if end not in edges:
                                edges.append(end)
                            end = edges.index(end)
                            graph[(start, end)] = weight

                graphs.append(graph)
                lineCount += 1

        # -- bgraph format --
        else:
            print("BGRAPH_2")

            edgesParsed = False

            if lineCount < len(lines):

                line = lines[lineCount]
                while lineCount + 1 < len(lines):
                    if not edgesParsed:
                        if line[0] != '#' and (" " not in line or "/" not in line) and line != "\n":
                            # each line represents a path
                            edges.append(line)
                            lineCount += 1
                            line = lines[lineCount]
                            continue
                        if line == "\n":
                            edgesParsed = True
                    else:

                        # line is now an empty line or it is null
                        # -- graphs --
                        lineCount += 1
                        line = lines[lineCount]
                        graphID = -1
                        graph = defaultdict(lambda: 0)
                        while lineCount + 1 < len(lines):
                            lineCount += 1
                            line = lines[lineCount]
                            graphID += 1

                            if graph:
                                graphs.append(graph)
                            if line[0] == '#':
                                labels.append(line[len(line) - 1])
                                lineCount += 1
                                line = lines[lineCount]
                            else:
                                labels.append(str(graphID))
                            graph = defaultdict(lambda: 0)

                            while lineCount + 1 < len(lines) and line != "\n":
                                stringList = line.split(' ')
                                if len(stringList) == 3:
                                    start = int(stringList[0])
                                    end = int(stringList[1])
                                    weight = float(stringList[2])
                                    graph[(start, end)] = weight
                                lineCount += 1
                                line = lines[lineCount]
                        graphs.append(graph)

        print("len(labels)")
        print(len(labels))
        print("len(graphs)")
        print(len(graphs))

        for i, graph in enumerate(graphs):
            graphData = []
            for s in range(len(edges)):
                for d in range(len(edges)):
                    graphData.append(graph[(s, d)])
            m.append(graphData)

    return np.array(m), labels
