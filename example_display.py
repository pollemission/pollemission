# Copyright (C) 2015, ENPC, INRIA
# Author(s): Ruiwei Chen, Vivien Mallet
#
# This file is part of a program for the computation of air pollutant
# emissions.
#
# This file is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this file. If not, see http://www.gnu.org/licenses/.

# This example file shows how to compute the hot emissions (in g) for
# passenger cars and display the emission level of streets with OpenStreetMap.

import matplotlib
matplotlib.use('Agg')

import os
import copert, osm_network
import numpy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

cop = copert.Copert("input/PC_parameter.csv", "input/LDV_parameter.csv",
                    "input/HDV_parameter.csv", "input/Moto_parameter.csv")

### Importing data files

# All text data files contain 25 lines, that is, one for each street.

# Description of the links in two columns: length in km and OpenStreetMap way
# ID. There is exactly one line per link.
data_link = numpy.loadtxt("input/link_osm.dat")
# Flow in veh/h; one line per link.
data_flow = numpy.loadtxt("input/flow.dat")
# Average travel speed in km/h; one line per link.
data_speed = numpy.loadtxt("input/speed.dat")

# Files for the description of the vehicle fleet. Always one line per link.
# Proportion of passenger cars.
data_passenger_proportion \
    = numpy.loadtxt("input/passenger_car_proportion.dat")

# Vehicle engine type.
engine_type = [cop.engine_type_gasoline, cop.engine_type_diesel]
# Proportion of gasoline cars -- the rest is assumed to be diesel.
data_gasoline_proportion = numpy.loadtxt("input/gasoline_proportion.dat")

# The three engine capacities are below 1.4 l, in [1.4 l, 2 l] and above 2
# l. In practice, we assign the following capacities (each of which falls
# uniquely in a category):
# engine_capacity = [1.3, 1.8, 2.1]
engine_capacity = [cop.engine_capacity_0p8_to_1p4,
                   cop.engine_capacity_1p4_to_2]

# Proportion of engines in each of the three capacities, for gasoline cars.
data_engine_capacity_gasoline \
    = numpy.loadtxt("input/engine_capacity_gasoline.dat")
# Proportion of engines in each of the three capacities, for diesel cars.
data_engine_capacity_diesel \
    = numpy.loadtxt("input/engine_capacity_diesel.dat")

# There are 14 COPERT categories, following the order from class 'Copert':
copert_class = [cop.class_PRE_ECE, cop.class_ECE_15_00_or_01,
                cop.class_ECE_15_02, cop.class_ECE_15_03, cop.class_ECE_15_04,
                cop.class_Improved_Conventional, cop.class_Open_loop,
                cop.class_Euro_1, cop.class_Euro_2, cop.class_Euro_3,
                cop.class_Euro_4, cop.class_Euro_5, cop.class_Euro_6,
                cop.class_Euro_6c]
Nclass = len(copert_class) # should be 14.
# Proportion of each COPERT class for gasoline cars.
data_copert_class_gasoline \
    = numpy.loadtxt("input/copert_class_proportion_gasoline.dat")
# Proportion of each COPERT class for diesel cars.
data_copert_class_diesel \
    = numpy.loadtxt("input/copert_class_proportion_diesel.dat")

### Computing the emissions

Nlink = data_link.shape[0]
hot_emission = numpy.zeros((Nlink, ), dtype = float)

for i in range(Nlink):
    v = min(max(10., data_speed[i]), 130.)
    link_length = data_link[i, 0]
    # Passenger car proportion.
    p_passenger = data_passenger_proportion[i]

    # Diesel and gasoline proportions.
    engine_type_distribution = [data_gasoline_proportion[i],
                                1. - data_gasoline_proportion[i]]
    engine_capacity_distribution = [data_engine_capacity_gasoline[i],
                                    data_engine_capacity_diesel[i]]

    for t in range(2): # gasoline/diesel
        for c in range(Nclass):
            for k in range(2): # engine capacities
                if (copert_class[c] != cop.class_Improved_Conventional
                    and copert_class[c] != cop.class_Open_loop) \
                    or engine_capacity[k] <= 2.0:
                    # No formula available for diesel passenger cars whose
                    # engine capacity is less than 1.4 l and the copert class
                    # is Euro 1, Euro 2 or Euro 3.
                    if t == 1 and k == 0 \
                       and copert_class[c] in range(cop.class_Euro_1,
                                                    1 + cop.class_Euro_3):
                        continue
                    e = cop.Emission(cop.pollutant_CO, v, link_length,
                                     cop.vehicle_type_passenger_car,
                                     engine_type[t],
                                     copert_class[c], engine_capacity[k], 20.)
                    e *= engine_type_distribution[t] \
                         * engine_capacity_distribution[t][k]
                    hot_emission[i] += e * p_passenger


### Plotting the emissions using OpenStreetMap
osm_file = "input/selected_zone-clermont.osm"

# Number of cores in use during the parsing of the OSM file.
Ncore = 8

# Tolerance for the search of node ids in the vicinity of the domain.
tolerance = 0.005

# Zoomed domain for plotting emissions
x_max = 3.084744
x_min = 3.079273
y_max = 45.790724
y_min = 45.787055

# Domain to be displayed.
selected_zone = [[x_min, y_max],
                 [x_min, y_min],
                 [x_max, y_min],
                 [x_max, y_max]]
selected_zone.append(selected_zone[0]) # to close the polygon.

# Retrieving the coordinates and IDs of the highways.
highway_coordinate, highway_osmid \
    = osm_network.retrieve_highway(osm_file, selected_zone, tolerance, Ncore)

# Line width associated to the largest emission.
s = 4.
width_scaling = s / hot_emission.max()
# Line width associated to the highways without known emissions.
sn = 0.5

color_scale  = colors.Normalize(vmin = 0, vmax = hot_emission.max())
scale_map = cmx.ScalarMappable(norm = color_scale)

# Get the OSM way IDs of the links.
emission_osm_id = [int(x) for x in data_link[:, 1]]

fig = plt.figure()

# Emissions.
ax = fig.add_axes([0.1, 0.1, 0.75, 0.75])
ax.set_aspect("equal", adjustable = "box")

# Colorbar.
ax_c = fig.add_axes([0.88, 0.1, 0.03, 0.8])
cb = matplotlib.colorbar.ColorbarBase(ax_c, cmap = matplotlib.cm.jet,
                                       norm = color_scale,
                                       orientation = "vertical")
cb.set_label("g")

# Loops over the highways (i.e., streets).
for refs, osmid in zip(highway_coordinate, highway_osmid):

    try:
        # Finding the emission link associated with the highway.
        i = emission_osm_id.index(osmid)
    except: # No emission on this highway.
        i = None

    if i != None:
        color_value = scale_map.to_rgba(hot_emission[i])
        ax.plot([x[0] for x in refs], [x[1] for x in refs],
                color = color_value,
                lw = hot_emission[i] * width_scaling)
    else: # no emission.
        ax.plot([x[0] for x in refs], [x[1] for x in refs],
                "k-", lw = sn)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.set_title("Emission map")

plt.savefig("output/map_CO_with_osm.png")
