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
# passenger cars at link resolution, and save them into text file.

import os
import copert
import numpy
import sys

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


f_emission_link = "output/link_hot_emission.txt"
numpy.savetxt(f_emission_link, hot_emission,  fmt = '%10.5f')

## END ##
