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

# This example file shows how to compute the emissions.

import copert

c = copert.Copert()

# Example for calculating hot emission (g/veh) of CO.
print c.Emission(pollutant = c.pollutant_CO,
                 speed = 40., # in km/h
                 distance = 0.5, # in km
                 vehicle_type = c.vehicle_type_passenger_car,
                 engine_type = c.engine_type_gasoline,
                 copert_class = c.class_ECE_15_00_or_01,
                 engine_capacity = 1.4, # in l
                 ambient_temperature = 20.) # in C deg

# Prints the hot emission factor (g/veh/km) of gasoline passenger car for CO.
print c.HEFGasolinePassengerCar(pollutant = c.pollutant_CO,
                                speed = 60., # in km/h
                                copert_class = c.class_Euro_4,
                                engine_capacity = 1.4) # in l
# Another way to compute the same is to call 'Emission' (g/veh) with unitary
# distance.
print c.Emission(pollutant = c.pollutant_CO,
                 speed = 60., # in km/h
                 distance = 1., # in km
                 vehicle_type = c.vehicle_type_passenger_car,
                 engine_type = c.engine_type_gasoline,
                 copert_class = c.class_Euro_4,
                 engine_capacity = 1.4, # in l
                 ambient_temperature = 20.) # in C deg
