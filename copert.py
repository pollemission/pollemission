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
import math


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
    class_Euro_3_GDI = 2.1
    class_Euro_4 = 3
    class_Euro_5 = 4
    class_Euro_6 = 5
    class_Euro_6c = 6

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


    # Definition of a general range of average speed for different road types,
    # in km/h.
    speed_type_urban = 60.
    speed_type_rural = 90.
    speed_type_highway = 130.


    # Data table (ref. EEA emission inventory guidebook 2013, part 1.A.3.b,
    # Road transportation, version updated in Sept. 2014, page 60, Table 3-41,
    # except for fuel consumption). It is assumed that if there is no value
    # for the coefficient in this table, the default value 0.0 will be taken.
    emission_factor_string \
        = """
1.12e1    1.29e-1  -1.02e-1  -9.47e-4  6.77e-4   0.0
6.05e1    3.50e0   1.52e-1   -2.52e-2  -1.68e-4  0.0
7.17e1    3.54e1   1.14e1    -2.48e-1  0.0       0.0
1.36e-1   -1.41e-2 -8.91e-4  4.99e-5   0.0       0.0
-1.35e-10 7.86e-8  -1.22e-5  7.75e-4   -1.97e-2  3.98e-1
-6.5e-11  4.78e-8  -7.79e-6  5.06e-4   -1.38e-2  3.54e-1
-4.42e-11 4.04e-8  -6.73e-6  4.34e-4   -1.17e-2  3.38e-1
1.35      1.78e-1  -6.77e-3  -1.27e-3  0.0       0.0
4.11e6    1.66e6   -1.45e4   -1.03e4   0.0       0.0
5.57e-2   3.65e-2  -1.1e-3   -1.88e-4  1.25e-5   0.0
1.18e-2   0.0      -3.47e-5  0.0       8.84e-7    0.0
2.87e-16  6.43     2.17e-2   -3.42e-1  0.0       0.0
-1.73e-12 7.45e-10 -9.59e-8  5.32e-6   -1.61e-4  8.98e-3
4.44e-13  -1.8e-10 5.08e-8   -5.31e-6  1.91e-4   5.3e-3
5.25e-1   0.0      -1e-2     0.0       9.36e-5   0.0
2.84e-1   -2.34e-2 -8.69e-3  4.43e-4   1.14e-4   0.0
9.29e-2   -1.22e-2 -1.49e-3  3.97e-5   6.53e-6   0.0
1.06e-1   0.0      -1.58e-3  0.0       7.1e-6    0.0
1.89e-1   1.57     8.15e-2   2.73e-2   -2.49e-4  -2.68e-1
4.74e-1   5.62     3.41e-1   8.38e-2   -1.52e-3  -1.19
9.99e14   1.89e16  1.31e15   2.9e14    -6.34e12  -4.03e15
NAN       NAN      NAN       NAN       NAN       NAN
NAN       NAN      NAN       NAN       NAN       NAN
NAN       NAN      NAN       NAN       NAN       NAN
NAN       NAN      NAN       NAN       NAN       NAN
1.44e-13  1.16e-10 -3.37e-8  3.11e-6   -1.25e-4  3.3e-3
2.31e-13  1.26e-11 -1.1e-8   1.23e-6   -6.29e-5  2.72e-3
2.65e-13  -4.07e-11 1.55e-9  1.43e-7   -2.5e-5   2.45e-3
"""
    # Emission factor coefficient ("efc"), for gasoline passenger cars.
    efc_gasoline_passenger_car \
        = numpy.fromstring(emission_factor_string, sep = ' ')
    efc_gasoline_passenger_car.shape = (4, 7, 6)


    # Data table (ref. EEA emission inventory guidebook 2013, part 1.A.3.b,
    # Road transportation, version updated in Sept. 2014, page 61, Table 3-41,
    # for fuel consummation FC).
    emission_factor_string \
        = """
1.91e2    1.29e-1   1.17     -7.23e-4  NAN       NAN
1.99e2    8.92e-2   3.46e-1  -5.38e-4  NAN       NAN
2.3e2     6.94e-2   -4.26e2  -4.46e-4  NAN       NAN
2.08e2    1.07e-1   -5.65e-1 -5.0e-4   1.43e-2   NAN
3.47e2    2.17e-1   2.73     -9.11e-4  4.28e-3   NAN
1.54e3    8.69e-1   1.91e1   -3.63e-3  NAN       NAN
1.7e2     9.28e-2   4.18e-1  -4.52e-4  4.99e-3   NAN
2.17e2    9.6e-2    2.53e-1  -4.21e-4  9.65e-3   NAN
2.53e2    9.02e-2   5.02e-1  -4.69e-4  NAN       NAN
1.1e2     2.61e-2   -1.67    2.25e-4   3.12e-2   NAN
1.36e2    2.6e2     -1.65    2.28e-4   3.12e-2   NAN
1.74e2    6.85e-2   3.64e-1  -2.47e-4  8.74e-3   NAN
2.85e2    7.28e-2   -1.37e-1 -4.16e-4  NAN       NAN
"""
    efc_gasoline_passenger_car_fc \
        = numpy.fromstring(emission_factor_string, sep = ' ')
    efc_gasoline_passenger_car_fc.shape = (1, 13, 6)


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


    # Definition of Hot Emission Factor (HEF) for gasoline passenger cars.
    def HEFGasolinePassengerCar(self, pollutant, speed, copert_class,
                                engine_capacity, **kwargs):
        """Computes the hot emissions factor in g/km for gasoline passenger
        cars, except for fuel consumption-dependent emissions (SO2, Pb,
        heavy metals).

        @param pollutant The pollutant for which the emissions are
        computed. It can be any of Copert.pollutant_*.

        @param speed The average velocity of the vehicles in kilometers per
        hour.

        @param copert_class The vehicle class, which can be any of the
        Copert.class_* attributes. They are introduced in the EMEP/EEA
        emission inventory guidebook.

        @param engine_capacity The engine capacity in liter.
        """

        V = speed

        if V == 0.0:
            return 0.0
        elif V < 10. or V > 130.:
            raise Exception, "There is no formula to calculate hot " \
                "emission factors when the speed is lower than 10 km/h " \
                "or higher than 130 km/h."
        else:
            if copert_class == self.class_PRE_ECE:
                if engine_capacity < 0.8:
                    raise Exception, "There is no formula to calculate hot "\
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if V < 100.:
                            return 281. * V**(-0.63)
                        else:
                            return 0.112 * V + 4.32
                    elif pollutant == self.pollutant_VOC:
                        if V < 100.:
                            return 30.34 * V**(-0.693)
                        else:
                            return 1.247
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return 1.173 + 0.0225 * V - 0.00014 * V**2
                        elif engine_capacity < 2.0:
                            return 1.360 + 0.0217 * V - 0.00004 * V**2
                        else:
                            return 1.5 + 0.03 * V + 0.0001 * V**2
            elif copert_class == self.class_ECE_15_00_or_01:
                if engine_capacity < 0.8:
                    raise Exception, "There is no formula to calculate hot "\
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if V < 50.:
                            return 313. * V**(-0.76)
                        else:
                            return 27.22 - 0.406 * V + 0.0032 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if V < 50.:
                            return 24.99 * V**(-0.704)
                        else:
                            return 4.85 * V**(-0.318)
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return 1.173 + 0.0225 * V - 0.00014 * V**2
                        elif engine_capacity < 2.0:
                            return 1.360 + 0.0217 * V - 0.00004 * V**2
                        else:
                            return 1.5 + 0.03 * V + 0.0001 * V**2
            elif copert_class == self.class_ECE_15_02:
                if engine_capacity < 0.8:
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if V < 60.:
                            return 300 * V**(-0.797)
                        else:
                            return 26.26 - 0.44 * V + 0.0026 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if V < 60.:
                            return 25.75 * V**(-0.714)
                        else:
                            return 1.95 - 0.019 * V + 0.00009 * V**2
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return 1.479 - 0.0037 * V + 0.00018 * V**2
                        elif engine_capacity < 2.0:
                            return 1.663 - 0.0038 * V + 0.0002 * V**2
                        else:
                            return 1.87 - 0.0039 * V + 0.00022 * V**2
            elif copert_class == self.class_ECE_15_03:
                if engine_capacity < 0.8:
                    raise Exception, "There is no formula to calculate hot "\
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if V < 20.:
                            return 161.36 - 45.62 * math.log(V)
                        else:
                            return 37.92 - 0.68 * V + 0.00377 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if V < 60.:
                            return 25.75 * V**(-0.714)
                        else:
                            return 1.95 - 0.019 * V + 0.00009 * V**2
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return 1.616 - 0.0084 * V + 0.00025 * V**2
                        elif engine_capacity < 2.0:
                            return 1.29 * math.exp(0.0099 * V)
                        else:
                            return 2.784 - 0.0112 * V + 0.000294 * V**2
            elif copert_class == self.class_ECE_15_04:
                if engine_capacity < 0.8:
                    raise Exception, "There is no formula to calculate hot "\
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if V < 60.:
                            return 260.788 * V**(-0.91)
                        else:
                            return 14.653 - 0.22 * V + 0.001163 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if V < 60.:
                            return 19.079 * V**(-0.693)
                        else:
                            return 2.608 - 0.037 * V + 0.000179 * V**2
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return 1.432 + 0.003 * V + 0.000097 * V**2
                        elif engine_capacity < 2.0:
                            return 1.484 + 0.013 * V + 0.000074 * V**2
                        else:
                            return 2.427 - 0.014 * V + 0.000266 * V**2
            elif copert_class == self.class_Improved_Conventional:
                if engine_capacity < 0.8 or engine_capacity > 2.0:
                    raise Exception, "There is no formula to calculate hot "\
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l " \
                        "or higher than 2.0 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if engine_capacity < 1.4:
                            return 14.577 - 0.294 * V + 0.002478 * V**2
                        else:
                            return 8.273 - 0.151 * V + 0.000957 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if engine_capacity < 1.4:
                            return 2.189 - 0.034 * V + 0.000201 * V**2
                        else:
                            return 1.999 - 0.034 * V + 0.000214 * V**2
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return -0.926 + 0.719 * math.log(V)
                        else:
                            return 1.387 + 0.0014 * V + 0.000247 * V**2
            elif copert_class == self.class_Open_loop:
                if engine_capacity < 0.8 or engine_capacity > 2.0:
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factor of gasoline passenger cars when " \
                        "the engine capacity is lower than 0.8 l " \
                        "or higher than 2.0 l."
                else:
                    if pollutant == self.pollutant_CO:
                        if engine_capacity < 1.4:
                            return 17.882 - 0.377 * V + 0.002825 * V**2
                        else:
                            return 9.446 - 0.230 * V + 0.002029 * V**2
                    elif pollutant == self.pollutant_VOC:
                        if engine_capacity < 1.4:
                            return 2.185 - 0.0423 * V + 0.000256 * V**2
                        else:
                            return 0.0808 - 0.016 * V + 0.000099 * V**2
                    elif pollutant == self.pollutant_NOx:
                        if engine_capacity < 1.4:
                            return -0.921 + 0.616 * math.log(V)
                        else:
                            return -0.761 + 0.515 * math.log(V)
            else:
                a, b, c, d, e, f \
                    = self.efc_gasoline_passenger_car[pollutant][copert_class]
                if copert_class <= self.class_Euro_4:
                    if pollutant != self.pollutant_PM:
                        return (a + c * V + e * V**2) / (1 + b * V + d * V**2)
                    else:
                        if copert_class <= self.class_Euro_2:
                            if V <= self.speed_type_urban:
                                return 3.22e-3
                            elif V <= self.speed_type_rural:
                                return 1.84e-3
                            else:
                                return 1.90e-3
                        elif copert_class <= self.class_Euro_4:
                            if V <= self.speed_type_urban:
                                return 1.28e-3
                            elif V <= self.speed_type_rural:
                                return 8.36e-4
                            else:
                                return 1.19e-3
                        else:
                            if V <= self.speed_type_urban:
                                return 6.6e-3
                            elif V <= self.speed_type_rural:
                                return 2.96e-3
                            else:
                                return 6.95e-3
                else:
                    if pollutant == self.pollutant_CO \
                       or pollutant == self.pollutant_PM:
                        return a * V**5 + b * V**4 + c * V**3 + d * V**2 \
                            + e * V + f
                    elif pollutant == self.pollutant_NOx:
                        return (a + c * V + e * V**2 + f / V) \
                            / (1 + b*V + d * V**2)
                    elif pollutant == self.pollutant_HC:
                        if copert_class == self.class_Euro_5:
                            return a * V**b + c * V**d
                        else:
                            return a * V**5 + b * V**4 + c * V**3 \
                                + d * V**2 + e * V + f
