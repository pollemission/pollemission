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


import numpy


class Copert:
    """
    This class implements COPERT formulae for road transport emissions.
    """


    # Definition of the vehicle classes used by COPERT.
    ## Pre-euro
    class_PRE_ECE = -7
    class_ECE_15_00_or_01 = -6
    class_ECE_15_02 = -5
    class_ECE_15_03 = -4
    class_ECE_15_04 = -3
    class_Improved_Conventional = -2
    class_Open_loop = -1
    ## Euro 1 and later
    class_Euro_1 = 0
    class_Euro_2 = 1
    class_Euro_3 = 2
    class_Euro_4 = 3
    class_Euro_5 = 4
    class_Euro_6 = 5
    class_Euro_6c = 7

    # Definition of the engine type used by COPERT.
    engine_type_gasoline = 0
    engine_type_diesel = 1
    engine_type_LPG = 2
    engine_type_two_stroke_gasoline = 3
    engine_type_hybrids = 4
    engine_type_E85 = 5
    engine_type_CNG = 6
    engine_type_moto_tow_stroke = 7
    engine_type_moto_four_stroke = 8

    # Definition of the vehicle type used by COPERT.
    vehicle_type_passenger_car = 0
    vehicle_type_light_commercial_vehicule = 1
    vehicle_type_heavy_duty_vehicle = 2
    vehicle_type_urban_bus = 3
    vehicle_type_coache = 4
    vehicle_type_moped_and_motorcycle_less_50 = 5
    vehicle_type_motocycle = 6

    # Definition of pollutant type used by COPERT.
    pollutant_CO = 0
    pollutant_HC = 1
    pollutant_NOx = 2
    pollutant_PM = 3
    pollutant_FC = 4
    pollutant_VOC = 5


    # Data table.
    emission_factor_string \
        = """
1.12e1  1.29e-1  -1.02e-1  -9.47e-4  6.77e-4   NAN
6.05e1  3.50e0   1.52e-1   -2.52e-2  -1.68e-4  NAN
"""
    # Emission factor coefficient, for gasoline passenger cars.
    efc_gasoline_passenger_car \
        = numpy.fromstring(emission_factor_string, sep = ' ')
    efc_gasoline_passenger_car.shape = (1, 2, 6)


    def __init__(self):
        """Constructor.
        """
        return


    def Emission(self, pollutant, speed, distance, vehicle_type, engine_type,
                 copert_class, engine_capacity, ambient_temperature,
                 **kwargs):
        """Computes the emissions in g.

        @param pollutant The pollutant for which the emissions are
        computed. It can be any of Copert.pollutant_*.

        @param speed The average velocity of the vehicles in kilometers per
        hour.

        @param distance The total distance covered by all the vehicles, in
        kilometers.

        @param vehicle_type The vehicle type, which can be any of the
        Copert.vehicle_type_*.

        @param engine_type The engine type, which can be any of the
        Copert.engine_type_*.

        @param copert_class The vehicle class, which can be any of the
        Copert.class_* attributes. They are introduced in the EMEP/EEA
        emission inventory guidebook.

        @param engine_capacity The engine capacity in liter.

        @param ambient_temperature The ambient temperature in Celsius degrees.
        """
        if pollutant == self.pollutant_CO:
            if speed == 0.0:
                return 0.0
            elif speed < 10. or speed > 130.:
                raise Exception, "There is no formula to calculate CO " \
                    "emission when the speed is lower than 10 km/h " \
                    "or higher than 130 km/h."
            else:
                if vehicle_type == self.vehicle_type_passenger_car:
                    if engine_type == self.engine_type_gasoline:
                        if copert_class == self.class_PRE_ECE:
                            if engine_capacity > 0.8:
                                if speed < 100.:
                                    return 281. * speed**(-0.63) * distance
                                else:
                                    return 0.112 * speed + 4.32
                            else:
                                raise Exception, "There is no formula to " \
                                    "calculate CO emission when engine " \
                                    "capacity is less than 0.8 l."
                        elif copert_class == self.class_ECE_15_00_or_01:
                            if engine_capacity > 0.8:
                                if speed <= 50.:
                                    return 313. * speed**(-0.76) * distance
                                else:
                                    return (27.22 - 0.406 * speed
                                            + 0.0032 * speed**2) * distance
                            else:
                                raise Exception, "There is no formula to " \
                                    "calculate CO emission when engine " \
                                    "capacity is less than 0.8 l."
