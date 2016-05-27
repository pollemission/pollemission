# Copyright (C) 2014, INRIA
# Author(s): Vivien Mallet
#
# This file is part of software for the data assimilation in the context of
# noise pollution at urban scale.
#
# This file is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this file. If not, see http://www.gnu.org/licenses/.

# This files retrieves the coordinates of the streets in the domain.


from imposm.parser import OSMParser
import numpy


# Determines whether a point is inside a given polygon or not.
# 'poly' is a list of (x, y) pairs.
# From: http://www.ariel.com.au/a/python-point-int-poly.html
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


# Simple class that handles the parsed OSM data in order to select the points
# inside the domain and the coordinates of the points around the domain. The
# domain is defined as a closed N-point polygon in 'selected_zone'
# (dimensions: N x 2).
class Point(object):
    def __init__(self, selected_zone, tolerance):
        # Copy of the selected domain.
        self.selected_zone = selected_zone
        # The list of points (ids) inside the zone.
        self.inside_zone = []
        # Coordinates, indexed by the OSM id.
        self.coordinate = {}

        # Coordinates of the rectangle that encloses the domain.
        self.x_min = min([x[0] for x in selected_zone]) - tolerance
        self.x_max = max([x[0] for x in selected_zone]) + tolerance
        self.y_min = min([x[1] for x in selected_zone]) - tolerance
        self.y_max = max([x[1] for x in selected_zone]) + tolerance

    def select(self, coord):
        for osmid, x, y in coord:
            # Selection of the points that are inside the domain.
            if point_inside_polygon(x, y, self.selected_zone):
                self.inside_zone.append(osmid)
            # Getting the ids of the coordinates inside the domain or in the
            # vicinity of the domain.
            if x < self.x_max and x > self.x_min \
                    and  y < self.y_max and y > self.y_min:
                self.coordinate[osmid] = (x, y)


# Simple class that handles the parsed OSM data in order to identify all
# streets that cross the domain.
class Highway(object):
    def __init__(self, point):
        # Set of all nodes inside the zone.
        self.point_inside_zone = set(point.inside_zone)
        # Points that describe the highways.
        self.point = []
        # Unsorted points that describe the highways, in a set.
        self.point_set = set()
        # Stores the OSM ID.
        self.osmid = []

    def select(self, ways):
        for osmid, tags, refs in ways:
            if "highway" in tags \
                    and not set(refs).isdisjoint(self.point_inside_zone):
                self.point.append(refs)
                self.osmid.append(osmid)


def retrieve_highway(osm_file, selected_zone, tolerance, Ncore = 1):
    # Parses the OSM file.
    point = Point(selected_zone, tolerance)
    p = OSMParser(concurrency = Ncore, coords_callback = point.select)
    p.parse(osm_file)

    highway = Highway(point)
    p = OSMParser(concurrency = Ncore, ways_callback = highway.select)
    p.parse(osm_file)

    highway.point_set = set([item for refs in highway.point for item in refs])

    # Getting all coordinates.
    point_coordinate = []
    for way in highway.point_set:
        try:
            point_coordinate.append(point.coordinate[way])
        except:
            pass

    # Defining the set of OSM way id and coordinates.
    highway_coordinate = []
    highway_osmid = []
    for refs, osmid in zip(highway.point, highway.osmid):
        try:
            highway_coordinate.append([point.coordinate[n] for n in refs])
            highway_osmid.append(osmid)
        except:
            pass

    return highway_coordinate, highway_osmid
