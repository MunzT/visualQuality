#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Detects and deals with intersections in the visualization of the projection.
"""

import numpy as np
import poly_point_isect

def getIntersections(X_embedded, timeLineLength, connectionLengths):

    minVal = np.min(X_embedded)  # 0
    maxVal = np.max(X_embedded)  # 1000

    scaleValue = (maxVal - minVal)  # TODO: assertion problem when values were too large -> e.g., scale to [0,1]
    segments = [(tuple((X_embedded[i] - minVal) / scaleValue), tuple((X_embedded[(i + 1)] - minVal) / scaleValue))
                for i in range(X_embedded.shape[0] - 1)]

    isect = poly_point_isect.isect_segments_include_segments(segments)

    ids = []
    intersections = []
    for intersection in isect:
        current_id = [i for i, x in enumerate(segments) if x == intersection[1][0] or x == intersection[1][1] or
                      x == intersection[1][0][::-1] or x == intersection[1][1][::-1]]
        ids.append(current_id)
        intersections.append(((intersection[0][0]) * scaleValue + minVal, (intersection[0][1]) * scaleValue + minVal))

    intersectionList = []

    if connectionLengths == 1:  # line connections
        # remove intersections created by the connection of multiple lines
        current = -1
        timeLineConnections = []
        for i in timeLineLength:
            current += i * connectionLengths
            timeLineConnections.append(current)

        for i, p in zip(ids, intersections):
            if not (i[0] in timeLineConnections or i[1] in timeLineConnections):
                s1 = 0
                index1 = i[0]
                for j in timeLineLength:
                    if index1 >= j:
                        s1 += 1
                        index1 -= j
                s2 = 0
                index2 = i[1]
                for j in timeLineLength:
                    if index2 >= j:
                        s2 += 1
                        index2 -= j

                currentIntersection = {"x": p[0], "y": p[1], "p1": 0, "p2": 0}

                if s1 < s2 and index1 < index2:
                    currentIntersection["seg1"] = index1
                    currentIntersection["seg2"] = index2
                    currentIntersection["ts1"] = s1
                    currentIntersection["ts2"] = s2
                    intersectionList.append(currentIntersection)
                else:
                    currentIntersection["seg1"] = index2
                    currentIntersection["seg2"] = index1
                    currentIntersection["ts1"] = s2
                    currentIntersection["ts2"] = s1
                    intersectionList.append(currentIntersection)

    else:  # catmull rom
        # remove intersections created by the connection of multiple lines
        current = -1
        timeLineConnections = []

        for i in timeLineLength:
            current += (i - 1) * connectionLengths + 1
            timeLineConnections.append(current)

        timeLineLength2 = []
        for i in timeLineLength:
            current = (i - 1) * connectionLengths + 1
            timeLineLength2.append(current)

        for i, p in zip(ids, intersections):
            if not (i[0] in timeLineConnections or i[1] in timeLineConnections):

                s1 = 0
                index1 = i[0]
                for j in timeLineLength2:
                    if index1 >= j:
                        s1 += 1
                        index1 -= j
                s2 = 0
                index2 = i[1]
                for j in timeLineLength2:
                    if index2 >= j:
                        s2 += 1
                        index2 -= j

                currentIntersection = {"x": p[0], "y": p[1]}

                if s1 < s2 or (s1 == s2 and index1 < index2) or\
                        (s1 == s2 and index1 == index2 and index1 % connectionLengths < index2 % connectionLengths):
                    currentIntersection["ts1"] = s1
                    currentIntersection["ts2"] = s2
                    currentIntersection["p1"] = index1 % connectionLengths
                    currentIntersection["p2"] = index2 % connectionLengths
                    currentIntersection["seg1"] = int(index1 / connectionLengths)
                    currentIntersection["seg2"] = int(index2 / connectionLengths)
                else:
                    currentIntersection["ts1"] = s2
                    currentIntersection["ts2"] = s1
                    currentIntersection["p1"] = index2 % connectionLengths
                    currentIntersection["p2"] = index1 % connectionLengths
                    currentIntersection["seg1"] = int(index2 / connectionLengths)
                    currentIntersection["seg2"] = int(index1 / connectionLengths)

                intersectionList.append(currentIntersection)

    intersectionList = sorted(intersectionList, key=lambda i: (i['ts2'], i['seg2'], i['p2']))

    return intersectionList
