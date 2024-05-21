#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Provides functions for interpolation: linear interpolation, Catmull Rom and Centripetal Catmull Rom.
"""

import math
import numpy as np

from dimRed import myTypes

"""
Add settings.subsampleCount samples between every two points; mainSamples contains the indices of the original samples.
"""
def addInterpolatedSamples(m, cS):

    print("Interpolation: {}...".format(cS.subsampleType))

    if cS.subsampleInHighDimSpace:
        numberOfInterpolations = []
        mainSamples = []

        if cS.subsampleCountFixed:
            numberOfInterpolations = [cS.subsampleCount for _ in range(len(m) - 1)]
        else:
            maxEl = 0
            for i in range(len(m) - 1):
                numberOfInterpolations.append(math.sqrt(sum((m[i] - m[i + 1]) ** 2)))
                maxEl = max(maxEl, numberOfInterpolations[-1])
            normalizer = maxEl / 10
            numberOfInterpolations[:] = [int(x / normalizer) for x in numberOfInterpolations]

        for i in range(len(m) - 1):
            for j in range(int(numberOfInterpolations[i] + 1)):
                mainSamples.append(j == 0)
        # last sample
        mainSamples.append(True)

        if cS.subsampleType == myTypes.SampleInterpolation.catmullRom:
            withInterpolations = CatmullRomChain(m, numberOfInterpolations)
            withInterpolations = [x for i in range(len(withInterpolations)) for x in withInterpolations[i]]
        elif cS.subsampleType == myTypes.SampleInterpolation.centripetalCatmullRom:
            withInterpolations = CentripetalCatmullRomChain(m, numberOfInterpolations)
            withInterpolations = [x for i in range(len(withInterpolations)) for x in withInterpolations[i]]
        else:
            withInterpolations = Linear(m, numberOfInterpolations)

        withInterpolations = np.array(withInterpolations)

        return withInterpolations, mainSamples

    print("...interpolation finished")
    return m, [True for _ in range(len(m))]

"""
Add nPoints samples between every two points using linear interpolation.
"""
def Linear(m, nPoints=100):
    if isinstance(nPoints, int):
        nPoints = [nPoints for _ in range(len(m) - 1)]

    withInterpolations = []
    i = 0
    for i in range(len(m) - 1):
        # interpolate between samples m[i] and m[i + 1]
        for j in range(nPoints[i] + 1):
            interpolated = m[i] + (m[i + 1] - m[i]) * j / (nPoints[i] + 1)
            withInterpolations.append(interpolated.tolist())

    # last sample
    withInterpolations.append(m[i + 1].tolist())

    print("...linear interpolation calculated")

    return withInterpolations

"""
Add nPoints samples between every two points using Catmull Rom.
"""
# https://de.switch-case.com/1251438
def CatmullRomChain(P, nPoints=100):

    if isinstance(nPoints, int):
        nPoints = [nPoints for _ in range(len(P) - 1)]

    sampleList = []

    front = P[0] - 0.01 * (P[1] - P[0])
    back = P[-1] - 0.01 * (P[-2] - P[-1])

    samples = CatmullRomSpline(front, P[0], P[1], P[2], nPoints[0] + 1)
    sampleList.append(samples.tolist())

    for j in range(1, len(P)-2):  # skip the ends
        p = CatmullRomSpline(P[j - 1], P[j], P[j + 1], P[j + 2], nPoints[j] + 1)
        sampleList.append(p.tolist())
        # draw p

    samples = CatmullRomSpline(P[-3], P[-2], P[-1], back, nPoints[-1] + 1)
    sampleList.append(samples.tolist())

    sampleList.append([P[-1].tolist()])

    print("...Catmull-Rom calculated...")

    return sampleList

"""
Calculates interpolated points on a Catmull Rom spline.
"""
def CatmullRomSpline(p_1, p0, p1, p2, nPoints=4):
    # wikipedia Catmull-Rom -> Cubic_Hermite_spline
    # 0 -> p0,  1 -> p1,  1/2 -> (- p_1 + 9 p0 + 9 p1 - p2)/16
    # assert 0 <= t <= 1

    samples = np.array([])
    for i in range(nPoints):  # t: 0 .1 .2 .. .9
        t = float(i)/nPoints
        value = (t*((2-t)*t - 1) * p_1
                    + (t*t*(3*t - 5) + 2) * p0
                    + t*((4 - 3*t)*t + 1) * p1
                    + (t-1)*t*t * p2)/2
        if samples.size == 0:
            samples = np.array([value])
        else:
            samples = np.append(samples, [value], axis=0)

    return samples

"""
Add nPoints samples between every two points using Centripetal Catmull Rom.
"""
def CentripetalCatmullRomChain(P, nPoints=100):
    """
    Code adopted from
    https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline

    Calculate Catmull Rom for a chain of points and return the combined curve.
    """

    if isinstance(nPoints, int):
        nPoints = [nPoints for _ in range(len(P) - 1)]

    sz = len(P)

    # The curve C will contain an array of (x,y) points.

    # first and last point shall be included as well
    front = P[0] - 0.01 * (P[1] - P[0])
    back = P[-1] - 0.01 * (P[-2] - P[-1])

    samples = CentripetalCatmullRomSpline(front, P[0], P[1], P[2], nPoints[0] + 2)
    sampleList = []
    sampleList.append(samples[:-1].tolist())

    for i in range(sz - 3):
        samples = CentripetalCatmullRomSpline(P[i], P[i + 1], P[i + 2], P[i + 3], nPoints[i + 1] + 2)
        sampleList.append(samples[:-1].tolist())

    samples = CentripetalCatmullRomSpline(P[-3], P[-2], P[-1], back, nPoints[-1] + 2)
    sampleList.append(samples[:-1].tolist())
    sampleList.append([P[-1].tolist()])

    print("...Centripetal Catmull-Rom calculated...")

    return sampleList

"""
Calculates points on a Centripetal Catmull Rom spline.
"""
def CentripetalCatmullRomSpline(P0, P1, P2, P3, nPoints=100):
    """
    Code from
    https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline

    P0, P1, P2, and P3 should be (x,y) point pairs that define the Catmull-Rom spline.
    nPoints is the number of points to include in this curve segment.
    """
    # Convert the points to numpy so that we can do array multiplication
    P0, P1, P2, P3 = map(np.array, [P0, P1, P2, P3])

    # Calculate t0 to t4
    alpha = 0.3

    def tj(ti, Pi, Pj):
        return (sum([((Pj[x] - Pi[x]) ** 2) for x in range(len(Pi))]) ** 0.5) ** alpha + ti

    t0 = 0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    # Only calculate points between P1 and P2
    t = np.linspace(t1, t2, nPoints)

    # Reshape so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    t = t.reshape(len(t), 1)

    A1 = (t1 - t) / (t1 - t0) * P0 + (t - t0) / (t1 - t0) * P1
    A2 = (t2 - t) / (t2 - t1) * P1 + (t - t1) / (t2 - t1) * P2
    A3 = (t3 - t) / (t3 - t2) * P2 + (t - t2) / (t3 - t2) * P3
    B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
    B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3

    C = (t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2
    return C
