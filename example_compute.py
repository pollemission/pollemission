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

c = copert.Copert("input/PC_parameter.csv", "input/LDV_parameter.csv",
                  "input/HDV_parameter.csv", "input/Moto_parameter.csv")

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
                                copert_class = c.class_Euro_5,
                                engine_capacity = 1.4) # in l
# Another way to compute the same is to call 'Emission' (g/veh) with unitary
# distance.
print c.Emission(pollutant = c.pollutant_CO,
                 speed = 60., # in km/h
                 distance = 1., # in km
                 vehicle_type = c.vehicle_type_passenger_car,
                 engine_type = c.engine_type_gasoline,
                 copert_class = c.class_Euro_5,
                 engine_capacity = 1.4, # in l
                 ambient_temperature = 20.) # in C deg


# Prints the hot emission factor (g/veh/km) of gasoline and diesel light
# commercial vehicles for CO.
## Gasoline light commercial vehicles
print c.HEFLightCommercialVehicle(pollutant = c.pollutant_CO,
                                  speed = 50.,
                                  engine_type = c.engine_type_gasoline,
                                  copert_class = c.class_Euro_5)

## Diesel light commercial vehicles
print c.HEFLightCommercialVehicle(pollutant = c.pollutant_CO,
                                  speed = 50.,
                                  engine_type = c.engine_type_diesel,
                                  copert_class = c.class_Euro_5)


# Prints the hot emission factor (g/veh/km) of gasoline and diesel heavy duty
# vehicles (HDVs) and buses for CO.
## for HDV
print c.HEFHeavyDutyVehicle(speed = 50,
                            vehicle_category = c.vehicle_type_heavy_duty_vehicle,
                            hdv_type = c.hdv_type_rigid_14_20,
                            hdv_copert_class = c.class_hdv_Euro_III,
                            pollutant = c.pollutant_CO,
                            load = c.hdv_load_50,
                            slope = c.slope_4)

## for buses
print c.HEFHeavyDutyVehicle(speed = 50,
                            vehicle_category = c.vehicle_type_bus,
                            hdv_type = c.bus_type_urban_18,
                            hdv_copert_class = c.class_hdv_Euro_III,
                            pollutant = c.pollutant_CO,
                            load = c.hdv_load_50,
                            slope = c.slope_4)

# Prints the emission factor for mopeds and motorcycles.
print c.EFMoped(speed = 50,
                pollutant = c.pollutant_CO,
                engine_type = c.engine_type_two_stroke_less_50,
                copert_class = c.class_Euro_3)

print c.EFMotorcycle(speed = 50,
                     pollutant = c.pollutant_CO,
                     engine_type = c.engine_type_four_stroke_more_750,
                     copert_class = c.class_Euro_3)
