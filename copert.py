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


    # Definition of the vehicle classes of emission standard used by COPERT.
    ## Pre-euro for passenger cars.
    class_PRE_ECE = 0
    class_ECE_15_00_or_01 = 1
    class_ECE_15_02 = 2
    class_ECE_15_03 = 3
    class_ECE_15_04 = 4
    class_Improved_Conventional = 5
    class_Open_loop = 6
    ## Euro 1 and later for passenger cars.
    class_Euro_1 = 7
    class_Euro_2 = 8
    class_Euro_3 = 9
    class_Euro_3_GDI = 10
    class_Euro_4 = 11
    class_Euro_5 = 12
    class_Euro_6 = 13
    class_Euro_6c = 14
    ## Print names for copert class
    name_class_euro = ["PRE_ECE", "ECE_15_00_or_01", "ECE_15_02", "ECE_15_03",
                       "ECE_15_04", "Improved_Conventional", "Open_loop",
                       "Euro_1", "Euro_2", "Euro_3", "Euro_3_GDI", "Euro_4",
                       "Euro_5", "Euro_6", "Euro_6c"]
    ## Pre-euro for heavy duty vehicles (hdv) and buses.
    class_hdv_Conventional = 0
    ## Euro 1 and later for heavy duty vehicles (hdv) and buses.
    class_hdv_Euro_I = 1
    class_hdv_Euro_II = 2
    class_hdv_Euro_III = 3
    class_hdv_Euro_IV = 4
    class_hdv_Euro_V_EGR = 5
    class_hdv_Euro_V_SCR = 6
    class_hdv_Euro_VI = 7
    ## Print names for Copert class of HDVs and buses.
    name_hdv_copert_class = ["Conventional", "Euro I", "Euro II",
                             "Euro III", "Euro IV", "Euro V - EGR",
                             "Euro V - SCR", "Euro VI"]

    # Definition of the engine type used by COPERT.
    engine_type_gasoline = 0
    engine_type_diesel = 1
    engine_type_LPG = 2
    engine_type_two_stroke_gasoline = 3
    engine_type_hybrids = 4
    engine_type_E85 = 5
    engine_type_CNG = 6
    engine_type_two_stroke_less_50 = 7
    engine_type_two_stroke_more_50 = 8
    engine_type_four_stroke_less_50 = 9
    engine_type_four_stroke_50_250 = 10
    engine_type_four_stroke_250_750 = 11
    engine_type_four_stroke_more_750 = 12

    # Definition of the engine capacity used by COPERT.
    engine_capacity_less_1p4 = 0
    engine_capacity_1p4_to_2 = 1
    engine_capacity_more_2 = 2

    # Definition of the vehicle type used by COPERT.
    vehicle_type_passenger_car = 0
    vehicle_type_light_commercial_vehicle = 1
    vehicle_type_heavy_duty_vehicle = 2
    vehicle_type_bus = 3
    vehicle_type_moped = 4
    vehicle_type_motorcycle = 5


    # Vehicle type of heavy duty vehicles (hdv) according to the loading
    # standard (Ref. the annex Excel file of the EEA Guidebook).
    ## For heavy duty vehicles (hdv).
    hdv_type_gasoline_3p5 = 0
    hdv_type_rigid_7p5 = 1
    hdv_type_rigid_7p5_12 = 2
    hdv_type_rigid_12_14 = 3
    hdv_type_rigid_14_20 = 4
    hdv_type_rigid_20_26 = 5
    hdv_type_rigid_26_28 = 6
    hdv_type_rigid_28_32 = 7
    hdv_type_rigid_32 = 8
    hdv_type_articulated_14_20 = 9
    hdv_type_articulated_20_28 = 10
    hdv_type_articulated_28_34 = 11
    hdv_type_articulated_34_40 = 12
    hdv_type_articulated_40_50 = 13
    hdv_type_articulated_50_60 = 14
    ## For buses and coaches.
    bus_type_urban_less_15 = 15
    bus_type_urban_15_18 = 16
    bus_type_urban_more_18 = 17
    bus_type_coach_standard_less_18 = 18
    bus_type_coach_articulated_more_18 = 19

    # Loading standards for heavy duty vehicles.
    hdv_load_0 = 0
    hdv_load_50 = 1
    hdv_load_100 = 2

    # Slope for roads
    slope_0 = 0
    slope_negative_6 = 1
    slope_negative_4 = 2
    slope_negative_2 = 3
    slope_2 = 4
    slope_4 = 5
    slope_6 = 6

    # Definition of pollutant type used by COPERT.
    pollutant_CO = 0
    pollutant_HC = 1
    pollutant_NOx = 2
    pollutant_PM = 3
    pollutant_FC = 4
    pollutant_VOC = 5

    # Printed Names.
    name_pollutant = ["CO", "HC", "NOx", "PM", "FC", "VOC"]

    # Definition of a general range of average speed for different road types,
    # in km/h.
    speed_type_urban = 60.
    speed_type_rural = 90.
    speed_type_highway = 130.

    # Basic generic functions.
    constant = lambda self, a : a
    linear = lambda self, a, b, x : a * x + b
    quadratic = lambda self, a, b, c, x : a * x**2 + b * x + c
    power = lambda self, a, b, x : a * x**b
    exponential = lambda self, a, b, x : a * math.exp(b * x)
    logarithm = lambda self, a, b, x : a + b * math.log(x)

    # Generic functions to calculate hot emissions factors for gasoline and
    # diesel passengers cars (ref. EEA emission inventory guidebook 2013, part
    # 1.A.3.b, Road transportation, version updated in Sept. 2014, page 60 and
    # page 65).
    EF_25 = lambda self, a, b, c, d, e, f, V : \
            (a + c * V + e * V**2) / (1 + b * V + d * V**2)
    EF_26 = lambda self, a, b, c, d, e, f, V : \
            a * V**5 + b * V**4 + c * V**3 + d * V**2 + e * V + f
    EF_27 = lambda self, a, b, c, d, e, f, V : \
            (a + c * V + e * V**2 + f / V) / (1 + b * V + d * V**2)
    EF_28 = lambda self, a, b, c, d, e, f, V : a * V**b + c * V**d
    EF_30 = lambda self, a, b, c, d, e, f, V: \
            (a + c * V + e * V**2) / (1 + b * V + d * V**2) + f / V
    EF_31 = lambda self, a, b, c, d, e, f, V : \
            a + (b / (1 + math.exp((-1*c) + d * math.log(V) + e * V)))

    # Generic function to calculate cold-start emission quotient (ref. EEA
    # emission inventory guidebook 2013, part 1.A.3.b, Road transportation,
    # version updated in Sept. 2014, page 62, table 3-43).
    cold_start_eq = lambda self, A, B, C, ta, V : \
                    A * V + B * ta + C

    # Generic functions to calculate hot emissions factors for passenger cars
    # and light commercial vehicles. (ref. the attached annex Excel file of
    # EMEP EEA emission inventory guidebook, updated September 2014).
    Eq_1 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           ((a + c * V + e * V**2 + f / V) / (1 + b * V + d * V**2)) \
           * (1-rf) + 0. * (g + h)
    Eq_2 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           ((a * V**2) + (b * V) + c + (d * math.log(V)) \
            + (e * math.exp(f * V)) +(g * (V**h))) * (1 - rf)
    Eq_3 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           (a + b * (1 + math.exp( - (V + c) / d ))**-1 ) * (1 - rf) \
           + 0. * (e + f + g + h)
    Eq_4 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           (a * V**b ) * (1- rf) + 0. * (c + d + e + f + g + h)
    Eq_5 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           (((a * V**2) + (b * V) + c + (d * math.log(V)) \
             + (e * math.exp(f * V)) + (g * (V**h))) * (1 - rf)) / 1000
    Eq_6 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           (a + b / (1 + math.exp((-1 * c \
                                     + d * math.log(V)) + e * V))) * (1 - rf)\
           + 0. * (f + g + h)
    Eq_7 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           ((a * V**3 + b * V**2) + c * V + d)* (1 - rf) + 0.* (e + f + g + h)
    Eq_8 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           ((a * b**V * V**c)) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_9 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
           ((a * V**b) + c * V**d) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_10 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (1 / (a + b * V**c)) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_11 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            ((a + b * V)**(-1 / c)) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_12 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (1 / (c * V**2 + b * V + a)) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_13 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            math.exp((a + b / V) + (c * math.log(V))) * (1 - rf) \
            + 0. * (d + e + f + g + h)
    Eq_14 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (e + a * math.exp(-1 * b * V) \
              + c * math.exp(-1 * d * V)) * (1 - rf) + 0. * (f + g + h)
    Eq_15 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (a * V**2 + b * V + c) * (1 - rf) + 0. * (d + e + f + g + h)
    Eq_16 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (a - b * math.exp(-1 * c * V**d)) * (1 - rf) + 0.* (e + f + g + h)
    Eq_17 = lambda self, a, b, c, d, e, f, g, h, rf, V : \
            (a * V**5 + b * V**4 + c * V**3 + d * V**2 + e * V + f) \
            * (1 - rf) + 0. * (g + h)

    list_equation_pc_ldv = [Eq_1, Eq_2, Eq_3, Eq_4, Eq_5, Eq_6, Eq_7, Eq_8,
                            Eq_9, Eq_10, Eq_11, Eq_12, Eq_13, Eq_14, Eq_15,
                            Eq_16, Eq_17]


    # Generic functions to calculate hot emissions factors for heavy duty
    # vehicles, buses and coaches. (ref. the attached annex Excel file of EMEP
    # EEA emission inventory guidebook, updated June 2012). The equation
    # numbers follow those of the annex file updated June 2012, not of those
    # of a later version or of the guidebook.
    Eq_hdv_0 = lambda self, a, b, c, d, e, f, g, x:\
               (a * (b**x)) * (x**c) + 0. * (d + e + f + g)
    Eq_hdv_1 = lambda self, a, b, c, d, e, f, g, x: \
               (a * (x**b)) + (c * (x**d))  + 0. * (e + f + g)
    Eq_hdv_2 = lambda self, a, b, c, d, e, f, g, x: \
               (a + (b * x))**((-1) / c) + 0. * (d + e + f + g)
    Eq_hdv_3 = lambda self, a, b, c, d, e, f, g, x: \
               (a + (b * x)) \
               + (((c - b) * (1 - math.exp(((-1) * d) * x))) / d) \
               + 0. * (e + f + g)
    Eq_hdv_4 = lambda self, a, b, c, d, e, f, g, x: \
               (e + (a * math.exp(((-1) * b) * x))) \
               + (c * math.exp(((-1) * d) * x)) \
               + 0. * (f + g)
    Eq_hdv_5 = lambda self, a, b, c, d, e, f, g, x: \
               1 / (((c * (x**2)) + (b * x)) + a)  + 0. * (d + e + f + g)
    Eq_hdv_6 = lambda self, a, b, c, d, e, f, g, x: \
               1 / (a + (b * (x**c))) + 0. * (d + e + f + g)
    Eq_hdv_7 = lambda self, a, b, c, d, e, f, g, x: \
               1 / (a + (b * x)) + 0. * (c + d + e + f + g)
    Eq_hdv_8 = lambda self, a, b, c, d, e, f, g, x: \
               a - (b * math.exp(((-1) * c) * (x**d))) + 0. * (e + f + g)
    Eq_hdv_9 = lambda self, a, b, c, d, e, f, g, x: \
               a / (1 + (b * math.exp(((-1) * c) * x))) + 0. * (d + e + f + g)
    Eq_hdv_10 = lambda self, a, b, c, d, e, f, g, x: \
                a + (b / (1 + math.exp(((-1 * c) + (d * math.log(x))) + (e * x))))\
                + 0. * (f + g)
    Eq_hdv_11 = lambda self, a, b, c, d, e, f, g, x: \
                c + (a * math.exp(((-1) * b) * x)) + 0. * (d + e + f + g)
    Eq_hdv_12 = lambda self, a, b, c, d, e, f, g, x: \
                c + (a * math.exp(b * x)) + 0. * (d + e + f + g)
    Eq_hdv_13 = lambda self, a, b, c, d, e, f, g, x: \
                math.exp((a + (b / x)) + (c * math.log(x))) \
                + 0. * (d + e + f + g)
    Eq_hdv_14 = lambda self, a, b, c, d, e, f, g, x: \
                ((a * (x**3)) + (b * (x**2)) + (c * x)) + d + 0. * (e + f + g)
    Eq_hdv_15 = lambda self, a, b, c, d, e, f, g, x: \
                ((a * (x**2)) + (b * x)) + c + 0. * (d + e + f + g)

    list_equation_hdv = [Eq_hdv_0, Eq_hdv_1, Eq_hdv_2,Eq_hdv_3, Eq_hdv_4,
                         Eq_hdv_5, Eq_hdv_6, Eq_hdv_7, Eq_hdv_8, Eq_hdv_9,
                         Eq_hdv_10, Eq_hdv_11, Eq_hdv_12, Eq_hdv_13,
                         Eq_hdv_14, Eq_hdv_15]


    # Generic functions to calculate hot emissions factors for two-stroke
    # motorcycles of engine displacement over 50 cm3.
    Eq_56 = lambda self, a0, a1, a2, a3, a4, a5, x: \
            a0 + a1 * x + a2 * x**2 + a3 * x**3 + a4 * x**4 + a5 * x**5


    # Data table to compute hot emission factor for gasoline passenger cars
    # from copert_class Euro1 to Euro 6c, except for FC. (ref. EEA emission
    # inventory guidebook 2013, part 1.A.3.b, Road transportation, version
    # updated in Sept. 2014, page 60, Table 3-41, except for fuel
    # consumption). It is assumed that if there is no value for the
    # coefficient in this table, the default value 0.0 will be taken.
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
    # Hot emission factor coefficient ("efc"), for gasoline passenger cars.
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


    # Data table for over-emission e_cold / e_hot for Euro 1 and later
    # gasoline vehicles(ref. EEA emission inventory guidebook 2013, part
    # 1.A.3.b, Road transportation, version updated in Sept. 2014, page 62,
    # Table 3-43).
    cold_start_emission_quotient_string \
        = """
0.156       -0.155      3.519
0.538       -0.373      -6.24
8.032e-2    -0.444      9.826
0.121       -0.146      3.766
0.299       -0.286      -0.58
5.03e-2     -0.363      8.604
7.82e-2     -0.105      3.116
0.193       -0.194      0.305
3.21e-2     -0.252      6.332
4.61e-2     7.38e-3     0.755
5.13e-2     2.34e-2     0.616
NAN         NAN         NAN
4.58e-2     7.47e-3     0.764
4.84e-2     2.28e-2     0.685
NAN         NAN         NAN
3.43e-2     5.66e-3     0.827
3.75e-2     1.72e-2     0.728
NAN         NAN         NAN
0.154       -0.134      4.937
0.323       -0.240      0.301
9.92e-2     -0.355      8.967
0.157       -0.207      7.009
0.282       -0.338      4.098
4.76e-2     -0.477      13.44
8.14e-2     -0.165      6.464
0.116       -0.229      5.739
1.75e-2     -0.346      10.462
"""
    cold_start_emission_quotient \
        = numpy.fromstring(cold_start_emission_quotient_string, sep = ' ')
    cold_start_emission_quotient.shape = (3, 3, 3, 3)

    # Data table to compute hot emission factor for diesel passenger cars from
    # copert_class Euro 1 to Euro 6c, except for FC.  (Ref. EEA emission
    # inventory guidebook 2013, part 1.A.3.b Road transportation, version
    # updated in Sept. 2014, page 65, Table 3-47) The categories of engine
    # capacity is < 1.4 l, 1.4 - 2.0 l, > 2.0 l.  If in the table, a line of
    # NAN signifies that there is no formula for calculating the emission
    # factor for this category of vehicle type or engine capacity according to
    # the coefficient table.  The "0.0" in the data table signifies vacant
    # values in table 3-47 of reference document.
    emission_factor_string \
        = """
NAN        NAN        NAN        NAN        NAN        NAN
9.96e-1    0.0        -1.88e-2   0.0        1.09e-4    0.0
9.96e-1    0.0        -1.88e-2   0.0        1.09e-4    0.0
NAN        NAN        NAN        NAN        NAN        NAN
9.00e-1    0.0        -1.74e-2   0.0        8.77e-5    0.0
9.00e-1    0.0        -1.74e-2   0.0        8.77e-5    0.0
NAN        NAN        NAN        NAN        NAN        NAN
1.69e-1    0.0        -2.92e-3   0.0        1.25e-5    1.1
1.69e-1    0.0        -2.92e-3   0.0        1.25e-5    1.1
NAN        NAN        NAN        NAN        NAN        NAN
NAN        NAN        NAN        NAN        NAN        NAN
NAN        NAN        NAN        NAN        NAN        NAN
-8.66e13   1.76e14    2.47e13    3.18e12    -1.94e11   8.33e13
-8.66e13   1.76e14    2.47e13    3.18e12    -1.94e11   8.33e13
-8.66e13   1.76e14    2.47e13    3.18e12    -1.94e11   8.33e13
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
-3.58e-11  1.23e-8    -1.49e-6   8.58e-5    -2.94e-3   1.03e-1
NAN        NAN        NAN        NAN        NAN        NAN
1.42e-1    1.38e-2    -2.01e-3   -1.90e-5   1.15e-5    0.0
1.59e-1    0.0        -2.46e-3   0.0        1.21e-5    0.0
NAN        NAN        NAN        NAN        NAN        NAN
1.61e-1    7.46e-2    -1.21e-3   -3.35e-4   3.63e-6    0.0
5.01e4     3.80e4     8.03e3     1.15e3     -2.66e1    0.0
NAN        NAN        NAN        NAN        NAN        NAN
9.65e-2    1.03e-1    -2.38e-4   -7.24e-5   1.93e-6    0.0
9.12e-2    0.0        -1.68e-3   0.0        8.94e-6    0.0
3.47e-2    2.69e-2    -6.41e-4   1.59e-3    1.12e-5    0.0
3.47e-2    2.69e-2    -6.41e-4   1.59e-3    1.12e-5    0.0
3.47e-2    2.69e-2    -6.41e-4   1.59e-3    1.12e-5    0.0
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
1.04e32    4.60e33    1.53e32    2.92e32    -3.83e28   1.96e32
NAN        NAN        NAN        NAN        NAN        NAN
3.1        1.41e-1    -6.18e-3   -5.03e-4   4.22e-4    0.0
3.1        1.41e-1    -6.18e-3   -5.03e-4   4.22e-4    0.0
NAN        NAN        NAN        NAN        NAN        NAN
2.4        7.67e-2    -1.16e-2   -5.0e-4    1.2e-4     0.0
2.4        7.67e-2    -1.16e-2   -5.0e-4    1.2e-4     0.0
NAN        NAN        NAN        NAN        NAN        NAN
2.82       1.98e-1    6.69e-2    -1.43e-3   -4.63e-4   0.0
2.82       1.98e-1    6.69e-2    -1.43e-3   -4.63e-4   0.0
1.11       0.0        -2.02e-2   0.0        1.48e-4    0.0
1.11       0.0        -2.02e-2   0.0        1.48e-4    0.0
1.11       0.0        -2.02e-2   0.0        1.48e-4    0.0
9.46e-1    4.26e-3    -1.14e-2   -5.15e-5   6.67e-5    1.92
9.46e-1    4.26e-3    -1.14e-2   -5.15e-5   6.67e-5    1.92
9.46e-1    4.26e-3    -1.14e-2   -5.15e-5   6.67e-5    1.92
4.36e-1    1.0e-2     -5.39e-3   -1.02e-4   2.90e-5    -4.61e-1
4.36e-1    1.0e-2     -5.39e-3   -1.02e-4   2.90e-5    -4.61e-1
4.36e-1    1.0e-2     -5.39e-3   -1.02e-4   2.90e-5    -4.61e-1
2.33e-1    1.00e-2    -2.88e-3   -1.02e-4   1.55e-5    -2.46e-1
2.33e-1    1.00e-2    -2.88e-3   -1.02e-4   1.55e-5    -2.46e-1
2.33e-1    1.00e-2    -2.88e-3   -1.02e-4   1.55e-5    -2.46e-1
NAN        NAN        NAN        NAN        NAN        NAN
1.14e-1    0.0        -2.33e-3   0.0        2.26e-5    0.0
1.14e-1    0.0        -2.33e-3   0.0        2.26e-5    0.0
NAN        NAN        NAN        NAN        NAN        NAN
8.66e-2    0.0        -1.42e-3   0.0        1.06e-5    0.0
8.66e-2    0.0        -1.42e-3   0.0        1.06e-5    0.0
NAN        NAN        NAN        NAN        NAN        NAN
5.15e-2    0.0        -8.8e-4    0.0        8.12e-6    0.0
5.15e-2    0.0        -8.8e-4    0.0        8.12e-6    0.0
4.50e-2    0.0        -5.39e-4   0.0        3.48e-6    0.0
4.50e-2    0.0        -5.39e-4   0.0        3.48e-6    0.0
4.50e-2    0.0        -5.39e-4   0.0        3.48e-6    0.0
1.17e-3    1.06e1     -6.48      5.67e-1    1.23e-2    0.0
1.17e-3    1.06e1     -6.48      5.67e-1    1.23e-2    0.0
1.17e-3    1.06e1     -6.48      5.67e-1    1.23e-2    0.0
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
-1.21e18   1.63e20    1.79e18    2.89e19    1.17e16    4.09e18
"""

    # Hot emission factor coefficient ("efc"), for diesel passenger cars.
    efc_diesel_passenger_car\
        = numpy.fromstring (emission_factor_string, sep = ' ')
    efc_diesel_passenger_car.shape = (4, 7, 3, 6)


    # Data table of the hot emission factor parameters for light commercial
    # vehicles ("ldv" for "light duty vehicles") of emission standard
    # Conventional and Euro 1. (ref. merged from Table 3-59 and Table 3-62)

    ldv_parameter_pre_euro_1_string \
        = """
10.0    110.0    0.01104    -1.5132    57.789
10.0    120.0    0.0037     -0.5215    19.127
10.0    110.0    0.0        0.0179     1.9547
10.0    120.0    7.55e-5    -0.009     0.666
10.0    110.0    67.7e-5    -0.117     5.4734
10.0    120.0    5.77e-5    -0.01047   0.54734
NAN     NAN      NAN        NAN        NAN
NAN     NAN      NAN        NAN        NAN
10.0    110.0    0.0167     -2.649     161.51
10.0    120.0    0.0195     -3.09      188.85
10.0    110.0    20e-5      -0.0256    1.8281
10.0    110.0    22.3e-5    -0.026     1.076
10.0    110.0    81.6e-5    -0.1189    5.1234
10.0    110.0    24.1e-5    -0.03181   2.0247
10.0    110.0    1.75e-5    -0.00284   0.2162
10.0    110.0    1.75e-5    -0.00284   0.2162
10.0    110.0    1.25e-5    -0.000577  0.288
10.0    110.0    4.5e-5     -0.004885  0.1932
10.0    110.0    0.02113    -2.65      148.91
10.0    110.0    0.0198     -2.506     137.42
"""
    ldv_parameter_pre_euro_1 \
        = numpy.fromstring(ldv_parameter_pre_euro_1_string, sep = ' ')
    ldv_parameter_pre_euro_1.shape = (2, 5, 2, 5)


    # Emission reduction percentage Euro 2 to Euro 4 light commercial vehicles
    # ("ldv" for "light duty vehicles") applied to vehicles of Euro 1. (data
    # merged from Table 3-60 and Table 3-63)
    ldv_reduction_percentage_string \
        = """
39.0    66.0    76.0    NAN
48.0    79.0    86.0    NAN
72.0    90.0    94.0    NAN
0.0     0.0     0.0     0.0
18.0    16.0    38.0    33.0
35.0    32.0    77.0    65.0
"""
    ldv_reduction_percentage \
        = numpy.fromstring(ldv_reduction_percentage_string, sep = ' ')
    ldv_reduction_percentage.shape = (2, 3, 4)


    # Data table of emission and fuel consumption factors for mopeds < 50 cm3.
    # (ref. data merged from table 3-67 and table 3-68)
    moped_parameter_string \
        = """
14.7    0.056    8.4     25.0     0.176
4.6     0.18     3.4     20.0     0.045
2.8     0.17     2.6     20.0     0.026
1.8     0.17     1.8     20.0     0.018
14.7    0.056    8.4     25.0     0.176
6.7     0.22     0.78    20.0     0.040
4.2     0.17     0.79    20.0     0.007
2.7     0.17     0.54    20.0     0.004
"""
    moped_parameter = numpy.fromstring(moped_parameter_string, sep = ' ')
    moped_parameter.shape = (2, 4, 5)


    def __init__(self, pc_parameter_file, ldv_parameter_file,
                 hdv_parameter_file, moto_parameter_file):
        """Constructor.
        """

        # Correspondence between strings and integer attributes in this class
        # for light commercial vehicles, heavy duty vehicles and buses.
        corr_pollutant = {"CO": self.pollutant_CO, "NOx": self.pollutant_NOx,
                          "HC": self.pollutant_HC, "PM": self.pollutant_PM,
                          "FC": self.pollutant_FC}
        self.index_pollutant = {self.pollutant_CO: 0, self.pollutant_NOx: 1,
                                self.pollutant_HC: 2, self.pollutant_PM: 3,
                                self.pollutant_FC: 4}

        # Updated hot emission factor coefficients and equations for gasoline
        # and diesel passenger cars (PC) with emission standard higher than
        # Euro 5. (Ref. the Excel file annex updated by Sept2014)
        self.pc_parameter = numpy.empty((7, 3, 4, 12), dtype = float)
        self.pc_parameter.fill(numpy.nan)
        ## Correspondence between strings and integer attributes for passenger
        ## cars.
        corr_pc_engine_type = {"Gasoline <0.8 l": 0,
                               "Gasoline 0.8 - 1.4 l": 1,
                               "Gasoline 1.4 - 2.0 l": 2,
                               "Gasoline >2.0 l": 3,
                               "Diesel <1.4 l": 4,
                               "Diesel 1.4 - 2.0 l": 5,
                               "Diesel >2.0 l": 6}
        corr_pc_class = {"5": self.class_Euro_5, "6": self.class_Euro_6,
                         "6c": self.class_Euro_6c}
        self.index_copert_class_pc = {self.class_Improved_Conventional: None,
                                      self.class_Euro_1: None,
                                      self.class_Euro_2: None,
                                      self.class_Euro_3: None,
                                      self.class_Euro_3_GDI: None,
                                      self.class_Euro_4: None,
                                      self.class_Euro_5: 0,
                                      self.class_Euro_6: 1,
                                      self.class_Euro_6c : 2}
        corr_pc_equation = {"Equation 1": 0, "Equation 6": 5,
                            "Equation 9": 8, "Equation 17": 16}
        pc_file = open(pc_parameter_file, "r")
        for line in pc_file.readlines():
            line_split = [s.strip() for s in line.split(",")]
            if line_split[0] == "Sector":
                continue
            i_pc_type = corr_pc_engine_type[line_split[1]]
            i_pc_copert_class \
                = self.index_copert_class_pc[corr_pc_class[line_split[3]]]
            i_pollutant = self.index_pollutant[corr_pollutant[line_split[4]]]
            line_split[16] = corr_pc_equation[line_split[16]]
            self.pc_parameter[i_pc_type, i_pc_copert_class, i_pollutant] \
                = [float(x) for x in line_split[5 : 17]]
        pc_file.close()

        # Hot emission factor coefficients and equations for light commercial
        # vehicles of emission standard higher than Euro 5. ("LDVs" for light
        # duty vehicles in the Excel file of the inventory guide book.)
        ## Initialization
        self.ldv_parameter = numpy.empty((2, 3, 5, 12), dtype = float)
        self.ldv_parameter.fill(numpy.nan)
        ## Correspondence between strings and integer attributes in this class
        ## for light commercial vehicles
        corr_ldv_type = {"Gasoline <3.5 t": self.engine_type_gasoline,
                         "Diesel <3.5 t": self.engine_type_diesel}
        corr_ldv_class = corr_pc_class
        self.index_copert_class_ldv = self.index_copert_class_pc

        corr_ldv_equation = {"Equation 1": 0, "Equation 9": 8,
                             "Equation 12": 11, "Equation 16": 15,
                             "Equation 17": 16}
        ldv_file = open(ldv_parameter_file, "r")
        for line in ldv_file.readlines():
            line_split = [s.strip() for s in line.split(",")]
            if line_split[0] == "Sector":
                continue
            i_ldv_type = corr_ldv_type[line_split[1]]
            i_ldv_copert_class \
                = self.index_copert_class_ldv[corr_ldv_class[line_split[3]]]
            i_pollutant = self.index_pollutant[corr_pollutant[line_split[4]]]
            line_split[16] = corr_ldv_equation[line_split[16]]
            self.ldv_parameter[i_ldv_type, i_ldv_copert_class, i_pollutant] \
                = [float(x) for x in line_split[5 : 17]]
        ldv_file.close()

        # Hot emission factor coefficients and equations for heavy duty
        # vehicles and buses.
        # Converting the CSV file into a multidimensional
        # array.  Initialization of parameters for heavy duty vehicles.
        self.hdv_parameter = numpy.empty((2, 20, 8, 5, 3, 7, 10),
                                         dtype = float)
        self.hdv_parameter.fill(numpy.nan)

        # Correspondence between strings and integer attributes in this class.
        corr_hdv_or_bus = {"HDV": self.vehicle_type_heavy_duty_vehicle,
                           "BUS": self.vehicle_type_bus}
        # Index of vehicle types of heavy duty vehicles (hdv) and buses.
        self.index_vehicle_type \
            = {self.vehicle_type_passenger_car: None,
               self.vehicle_type_light_commercial_vehicle: None,
               self.vehicle_type_heavy_duty_vehicle: 0,
               self.vehicle_type_bus: 1,
               self.vehicle_type_moped: None,
               self.vehicle_type_motorcycle: None}
        self.corr_hdv_type \
            =  {"Gasoline >3.5 t": self.hdv_type_gasoline_3p5,
                "Rigid <=7.5 t": self.hdv_type_rigid_7p5,
                "Rigid 7.5 - 12 t": self.hdv_type_rigid_7p5_12,
                "Rigid 12 - 14 t": self.hdv_type_rigid_12_14,
                "Rigid 14 - 20 t": self.hdv_type_rigid_14_20,
                "Rigid 20 - 26 t": self.hdv_type_rigid_20_26,
                "Rigid 26 - 28 t": self.hdv_type_rigid_26_28,
                "Rigid 28 - 32 t": self.hdv_type_rigid_28_32,
                "Rigid >32 t": self.hdv_type_rigid_32,
                "Articulated 14 - 20 t": self.hdv_type_articulated_14_20,
                "Articulated 20 - 28 t": self.hdv_type_articulated_20_28,
                "Articulated 28 - 34 t": self.hdv_type_articulated_28_34,
                "Articulated 34 - 40 t": self.hdv_type_articulated_34_40,
                "Articulated 40 - 50 t": self.hdv_type_articulated_40_50,
                "Articulated 50 - 60 t": self.hdv_type_articulated_50_60,
                "Urban Buses Midi <=15 t": self.bus_type_urban_less_15,
                "Urban Buses Standard 15 - 18 t": self.bus_type_urban_15_18,
                "Urban Buses Articulated >18 t": self.bus_type_urban_more_18,
                "Coaches Standard <=18 t": self.bus_type_coach_standard_less_18,
                "Coaches Articulated >18 t": self.bus_type_coach_articulated_more_18}
        corr_tech = {"Conventional": self.class_hdv_Conventional,
                     "HD Euro I": self.class_hdv_Euro_I,
                     "HD Euro II": self.class_hdv_Euro_II,
                     "HD Euro III": self.class_hdv_Euro_III,
                     "HD Euro IV": self.class_hdv_Euro_IV,
                     "HD Euro V - EGR": self.class_hdv_Euro_V_EGR,
                     "HD Euro V - SCR": self.class_hdv_Euro_V_SCR,
                     "HD Euro VI": self.class_hdv_Euro_VI}
        self.corr_load = {"0": self.hdv_load_0,
                          "50": self.hdv_load_50,
                          "100": self.hdv_load_100}
        self.corr_slope = {"0%": self.slope_0,
                           "-6%": self.slope_negative_6,
                           "-4%": self.slope_negative_4,
                           "-2%": self.slope_negative_2,
                           "2%": self.slope_2,
                           "4%": self.slope_4,
                           "6%": self.slope_6}
        hdv_file = open(hdv_parameter_file, "r")
        for line in hdv_file.readlines():
            line_split = [s.strip() for s in line.split(",")]
            if line_split[0] == "Type":
                continue
            if "-" in line_split[3]:
                index = line_split[3].index("-")
                if line_split[3][:index] != "HD Euro V ":
                    hdv_tech = line_split[3][:index - 1]
                else:
                    hdv_tech = line_split[3]
            else:
                hdv_tech = line_split[3]
            i_hdv_or_bus \
                = self.index_vehicle_type[corr_hdv_or_bus[line_split[0]]]
            i_hdv_type = self.corr_hdv_type[line_split[1]]
            i_hdv_tech = corr_tech[hdv_tech]
            i_pollutant = self.index_pollutant[corr_pollutant[line_split[4]]]
            i_hdv_load = self.corr_load[line_split[5]]
            i_hdv_slope = self.corr_slope[line_split[6]]
            self.hdv_parameter[i_hdv_or_bus, i_hdv_type, i_hdv_tech,
                               i_pollutant, i_hdv_load, i_hdv_slope] \
                = [float(x) for x in line_split[8 : 18]]
        hdv_file.close()

        # Emission factor coefficients for motorcycles of engine displacement
        # over 50 cm3. The data in the text file is based on the Table 3-69,
        # Table 3-70, Table 3-71.
        ## Initialization
        self.moto_parameter = numpy.empty((4, 5, 4, 8), dtype = float)
        self.moto_parameter.fill(numpy.nan)
        ## Correspondence between strings and integer attributes in this class
        ## for motorcycles
        self.corr_engine_type \
            = {"2-Stroke": self.engine_type_two_stroke_more_50,
               "4-Stroke < 250": self.engine_type_four_stroke_50_250,
               "4-Stroke 250-750": self.engine_type_four_stroke_250_750,
               "4-Stroke > 750": self.engine_type_four_stroke_more_750}
        self.index_moto_engine_type \
            = {self.engine_type_two_stroke_more_50: 0,
               self.engine_type_four_stroke_50_250: 1,
               self.engine_type_four_stroke_250_750: 2,
               self.engine_type_four_stroke_more_750: 3}
        corr_copert_class \
            = {"Conventional": self.class_Improved_Conventional,
               "Euro 1": self.class_Euro_1, "Euro 2": self.class_Euro_2,
               "Euro 3": self.class_Euro_3}
        self.index_copert_class_moto = {self.class_Improved_Conventional: 0,
                                        self.class_Euro_1: 1,
                                        self.class_Euro_2: 2,
                                        self.class_Euro_3: 3}
        ## Converting the CSV file into a multidimensional array.
        moto_file = open(moto_parameter_file, "r")
        for line in moto_file.readlines():
            line_split = [s.strip() for s in line.split(",")]
            if line_split[0] == "Engine type":
                continue
            i_engine_type \
                = self.index_moto_engine_type[self.corr_engine_type[line_split[0]]]
            i_pollutant = self.index_pollutant[corr_pollutant[line_split[1]]]
            i_copert_class \
                = self.index_copert_class_moto[corr_copert_class[line_split[2]]]
            self.moto_parameter[i_engine_type, i_pollutant,
                                i_copert_class] \
                = [float(x) for x in line_split[3 : 11]]
        moto_file.close()
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
        if vehicle_type == self.vehicle_type_passenger_car:
            if engine_type == self.engine_type_gasoline:
                return distance \
                    * self.HEFGasolinePassengerCar(pollutant, speed,
                                                   copert_class,
                                                   engine_capacity, **kwargs)
            elif engine_type == self.engine_type_diesel:
                return distance \
                    * self.HEFDieselPassengerCar(pollutant, speed,
                                                 copert_class,
                                                 engine_capacity, **kwargs)
            else:
                raise Exception, "Only emission factors for gasoline and " \
                    + "diesel vehicles are available."
        else:
            raise Exception, "Only emission factors for passenger cars " \
                + "are available."


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

        if speed == 0.0:
            return 0.0
        else:
            V = speed
            if copert_class <= self.class_Euro_4:
                if V < 10. or V > 130. :
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factors when the speed is lower than " \
                        "10 km/h or higher than 130 km/h for passenger " \
                        "cars with emission standard lower than Euro 4."
                else:
                    if copert_class == self.class_PRE_ECE:
                        if engine_capacity < 0.8:
                            raise Exception, "There is no formula to "\
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity is "\
                                "lower than 0.8 l with emission standard " \
                                "of PRE ECE."
                        else:
                            if pollutant == self.pollutant_CO:
                                if V < 100.:
                                    return self.power(281., -0.63, V)
                                else:
                                    return self.linear(0.112, 4.32, V)
                            elif pollutant == self.pollutant_VOC:
                                if V < 100.:
                                    return self.power(30.34, -0.693, V)
                                else:
                                    return self.constant(1.247)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.quadratic(-0.00014, 0.0225,
                                                          1.173, V)
                                elif engine_capacity < 2.0:
                                    return self.quadratic(-0.00004, 0.0217,
                                                          1.360, V)
                                else:
                                    return self.quadratic(0.0001, 0.03,
                                                          1.5, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "standard of pre-Euro."
                                return None
                    elif copert_class == self.class_ECE_15_00_or_01:
                        if engine_capacity < 0.8:
                            raise Exception, "There is no formula to "\
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity " \
                                "is lower than 0.8 l with emission standard "\
                                "of ECE 15-00/01."
                        else:
                            if pollutant == self.pollutant_CO:
                                if V < 50.:
                                    return self.power(313., -0.76, V)
                                else:
                                    return self.quadratic(0.0032, -0.406,
                                                          27.22, V)
                            elif pollutant == self.pollutant_VOC:
                                if V < 50.:
                                    return self.power(24.99, -0.704, V)
                                else:
                                    return self.power(4.85, -0.318, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.quadratic(-0.00014, 0.0225,
                                                          1.173, V)
                                elif engine_capacity < 2.0:
                                    return self.quadratic(-0.00004, 0.0217,
                                                          1.360, V)
                                else:
                                    return self.quadratic(0.0001, 0.03,
                                                          1.5, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "standard of pre-Euro."
                                return None
                    elif copert_class == self.class_ECE_15_02:
                        if engine_capacity < 0.8:
                            raise Exception, "There is no formula to "\
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity " \
                                "is lower than 0.8 l with emission standard "\
                                "of ECE 15-02."
                        else:
                            if pollutant == self.pollutant_CO:
                                if V < 60.:
                                    return self.power(300, -0.797, V)
                                else:
                                    return self.quadratic(0.0026, -0.44,
                                                          26.26, V)
                            elif pollutant == self.pollutant_VOC:
                                if V < 60.:
                                    return self.power(25.75, -0.714, V)
                                else:
                                    return self.quadratic(0.00009, -0.019,
                                                          1.95, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.00018, -0.0037,
                                                          1.479, V)
                                elif engine_capacity < 2.0:
                                    return self.quadratic(0.0002, -0.0038,
                                                          1.663, V)
                                else:
                                    return self.quadratic(0.00022, -0.0039,
                                                          1.87, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "standard of pre-Euro."
                                return None
                    elif copert_class == self.class_ECE_15_03:
                        if engine_capacity < 0.8:
                             raise Exception, "There is no formula to "\
                                 "calculate hot emission factor of gasoline " \
                                 "passenger cars when the engine capacity " \
                                 "is lower than 0.8 l with emission standard "\
                                 "of ECE 15-03."
                        else:
                            if pollutant == self.pollutant_CO:
                                if V < 20.:
                                    return self.logarithm(161.36, -45.62, V)
                                else:
                                    return self.quadratic(0.00377, -0.68,
                                                          37.92, V)
                            elif pollutant == self.pollutant_VOC:
                                if V < 60.:
                                    return self.power(25.75, -0.714, V)
                                else:
                                    return self.quadratic(0.00009, -0.019,
                                                          1.95, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.00025, -0.0084,
                                                          1.616, V)
                                elif engine_capacity < 2.0:
                                    return self.exponential(1.29, 0.0099, V)
                                else:
                                    return self.quadratic(0.000294, -0.0112,
                                                          2.784, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "standard of pre-Euro."
                                return None
                    elif copert_class == self.class_ECE_15_04:
                        if engine_capacity < 0.8:
                            raise Exception, "There is no formula to "\
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity " \
                                "is lower than 0.8 l with emission standard "\
                                "of ECE 15-04."
                        else:
                            if pollutant == self.pollutant_CO:
                                if V < 60.:
                                    return self.power(260.788, -0.91, V)
                                else:
                                    return self.quadratic(0.001163, -0.22,
                                                          14.653, V)
                            elif pollutant == self.pollutant_VOC:
                                if V < 60.:
                                    return self.power(19.079, -0.693, V)
                                else:
                                    return self.quadratic(0.000179, -0.037,
                                                          2.608, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.000097, 0.003,
                                                          1.432, V)
                                elif engine_capacity < 2.0:
                                    return self.quadratic(0.000074, 0.013,
                                                          1.484, V)
                                else:
                                    return self.quadratic(0.000266, -0.014,
                                                          2.427, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "standard of pre-Euro."
                                return None
                    elif copert_class == self.class_Improved_Conventional:
                        if engine_capacity < 0.8 or engine_capacity > 2.0:
                            raise Exception, "There is no formula to " \
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity " \
                                "is lower than 0.8 l or higher than 2.0 l " \
                                "for vehicle technology of Improved " \
                                "Conventional cars."
                        else:
                            if pollutant == self.pollutant_CO:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.002478, -0.294,
                                                          14.577, V)
                                else:
                                    return self.quadratic(0.000957, -0.151,
                                                          8.273, V)
                            elif pollutant == self.pollutant_VOC:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.000201, -0.034,
                                                          2.189, V)
                                else:
                                    return self.quadratic(0.000214, -0.034,
                                                          1.999, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.logarithm(-0.926, 0.719, V)
                                else:
                                    return self.quadratic(0.000247, 0.0014,
                                                          1.387, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "emission standard of pre-Euro."
                                return None
                    elif copert_class == self.class_Open_loop:
                        if engine_capacity < 0.8 or engine_capacity > 2.0:
                            raise Exception, "There is no formula to "\
                                "calculate hot emission factor of gasoline " \
                                "passenger cars when the engine capacity " \
                                "is lower than 0.8 l or higher than 2.0 l " \
                                "for vehicle technology Open loop."
                        else:
                            if pollutant == self.pollutant_CO:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.002825, -0.377,
                                                          17.882, V)
                                else:
                                    return self.quadratic(0.002029, -0.230,
                                                          9.446, V)
                            elif pollutant == self.pollutant_VOC:
                                if engine_capacity < 1.4:
                                    return self.quadratic(0.000256, -0.0423,
                                                          2.185, V)
                                else:
                                    return self.quadratic(0.000099, -0.016,
                                                          0.808, V)
                            elif pollutant == self.pollutant_NOx:
                                if engine_capacity < 1.4:
                                    return self.logarithm(-0.921, 0.616, V)
                                else:
                                    return self.logarithm(-0.761, 0.515, V)
                            else:
                                raise Exception, "Only formulas for CO, " \
                                    "VOC, NOx are available for emission " \
                                    "emission standard of pre-Euro."
                                return None

                    else:
                        if pollutant == self.pollutant_PM:
                            if copert_class <= self.class_Euro_2:
                                if V <= self.speed_type_urban:
                                    return self.constant(3.22e-3)
                                elif V <= self.speed_type_rural:
                                    return self.constant(1.84e-3)
                                else:
                                    return self.constant(1.90e-3)
                            elif copert_class == self.class_Euro_3_GDI:
                                if V <= self.speed_type_urban:
                                    return self.constant(6.6e-3)
                                elif V <= self.speed_type_rural:
                                    return self.constant(2.96e-3)
                                else:
                                    return self.constant(6.95e-3)
                            else:
                                if V <= self.speed_type_urban:
                                    return self.constant(1.28e-3)
                                elif V <= self.speed_type_rural:
                                    return self.constant(8.36e-4)
                                else:
                                    return self.constant(1.19e-3)
                        else:
                            # Global indexes of EURO classes, ordered by
                            # appearance in the guidebook.
                            global_class_index \
                                = [self.class_Euro_1, self.class_Euro_2,
                                   self.class_Euro_3, self.class_Euro_4]
                            copert_index \
                                = global_class_index.index(copert_class)
                            a, b, c, d, e, f \
                                = self.efc_gasoline_passenger_car[pollutant][copert_index]
                            return self.EF_25(a, b, c, d, e, f, V)
            else:
                if engine_capacity < 0.8:
                    i_engine = 0
                elif engine_capacity >= 0.8 and engine_capacity < 1.4:
                    i_engine = 1
                elif engine_capacity >= 1.4 and engine_capacity < 2.0:
                    i_engine = 2
                else:
                    i_engine = 3
                i_copert_class = self.index_copert_class_pc[copert_class]
                if pollutant == self.pollutant_VOC \
                   or pollutant == self.pollutant_FC:
                    raise Exception, "There is no formula to calculate " \
                        "hot emission factors of VOC and FC for " \
                        "gasoline passenger cars of emission standard "\
                        "higher than Euro 5 (included)."
                else:
                    i_pollutant = self.index_pollutant[pollutant]
                a, b, c, d, e, f, g, h, rf, Vmin, Vmax, N_eq \
                    = self.pc_parameter[i_engine, i_copert_class, i_pollutant]
                if V < Vmin or V > Vmax:
                    raise Exception, "The input speed must be in the range " \
                        + "of [" + str(round(Vmin, 1)) + ", " \
                        + str(round(Vmax, 1)) + "] when calculating hot " \
                        "emission factors for passenger cars with emission " \
                        "standard of Euro 5 or higher."
                emission_factor \
                    = self.list_equation_pc_ldv[int(N_eq)](self, a, b, c, d,
                                                           e, f, g, h, rf, V)
                return emission_factor


    # Definition of cold-start emission quotient (e_cold / e_hot).
    def ColdStartEmissionQuotient(self, vehicle_type, engine_type, pollutant,
                                  speed, copert_class, engine_capacity,
                                  ambient_temperature, **kwargs):
        V = speed
        if (vehicle_type == self.vehicle_type_passenger_car or \
            vehicle_type == self.vehicle_type_light_commercial_vehicle):
            if engine_type == self.engine_type_gasoline:
               if vehicle_type == self.vehicle_type_passenger_car:
                   if copert_class < self.class_Euro_1:
                       if ambient_temperature < -10:
                           raise Exception, "There is no formula for " \
                               "calculating the cold-start emission " \
                               "quotient when the ambient temperature is " \
                               "lower than -10.0 Celsius degrees. "
                       elif ambient_temperature > 30:
                           return 1.0
                       else:
                           if pollutant == self.pollutant_CO:
                               return 3.7 - 0.09 * ambient_temperature
                           elif pollutant == self.pollutant_NOx:
                               return 1.14 - 0.006 * ambient_temperature
                           elif pollutant == self.pollutant_VOC:
                               return 2.8 - 0.06 * ambient_temperature
                           elif pollutant == self.pollutant_FC:
                               return 1.47 - 0.009 * ambient_temperature
                           else:
                               raise Exception, "There is no formula to " \
                                   "calculate the cold start emission "\
                                   "quotient for conventional gasoline " \
                                   "passenger cars or light commercial " \
                                   "vehicles, for pollutants of HC or PM."
                   else:
                       if pollutant == self.pollutant_FC:
                           if ambient_temperature < -10:
                               raise Exception, "There is no formula to " \
                                   "calculate the cold-start emission " \
                                   "quotient when the ambient temperature " \
                                   "is lower than -10.0 Celsius degrees. "
                           elif ambient_temperature > 30:
                               return 1.0
                           else:
                               return -0.009 * ambient_temperature + 1.47
                       elif pollutant == self.pollutant_PM \
                       or pollutant == self.pollutant_HC:
                           raise Exception, "There is no formula to " \
                               "calculate the cold start emission quotient " \
                               "for conventional gasoline passenger " \
                               "cars, or light commercial vehicles, for " \
                               "pollutants of HC or PM."
                       else:
                           if V < 5 or V > 45 or ambient_temperature < -20:
                               raise Exception, "To calculate the cold " \
                                   "start emission quotient for CO and NOx, "\
                                   "the vehicle average speed must be in " \
                                   "range [5, 45] and the ambient " \
                                   "temperature must be higher than -20 " \
                                   "Celsius degrees. "
                           else:
                               index_pollutant = {self.pollutant_CO: 0,
                                                  self.pollutant_NOx: 1,
                                                  self.pollutant_VOC: 2}
                               i_pollu = index_pollutant[pollutant]
                               index_engine_capacity \
                                   = { self.engine_capacity_0p8_to_1p4: 0,
                                       self.engine_capacity_1p4_to_2: 1,
                                       self.engine_capacity_more_2: 2}
                               i_engine_k \
                                   = index_engine_capacity[engine_capacity]
                               if pollutant == self.pollutant_CO \
                                  or pollutant == self.pollutant_VOC :
                                   if V <= 25 and ambient_temperature <= 15:
                                       i_v_ta = 0
                                   elif V > 25 and ambient_temperature <= 15:
                                       i_v_ta = 1
                                   else:
                                       i_v_ta = 2
                               else:
                                   if V <= 25:
                                       i_v_ta = 0
                                   else:
                                       i_v_ta = 1
                               A, B, C \
                                   = self.cold_start_emission_quotient[i_pollu,
                                                                       i_engine_k,
                                                                       i_v_ta]
                               return self.cold_start_eq(A, B, C,
                                                         ambient_temperature,
                                                         V)
               else:
                   e_cold_passenger \
                       = self.ColdStartEmissionQuotient(self.vehicle_type_passenger_car,
                                                        self.engine_type_gasoline,
                                                        pollutant,
                                                        speed, copert_class,
                                                        engine_capacity,
                                                        ambient_temperature)
                   e_cold_passenger_engine_more_2 \
                       = self.ColdStartEmissionQuotient(self.vehicle_type_passenger_car,
                                                        self.engine_type_gasoline,
                                                        pollutant,
                                                        speed, copert_class,
                                                        self.engine_capacity_more_2,
                                                        ambient_temperature)
                   if copert_class < self.class_Euro_1:
                       return e_cold_passenger
                   else:
                       return e_cold_passenger_engine_more_2
            elif engine_type == self.engine_type_diesel:
                if ambient_temperature < -10.0:
                    raise Exception, "There is no formula " \
                        "for calculating the cold-start emission " \
                        "quotient when the ambient temperature is " \
                        "lower than -10.0 Celsius degrees. "
                elif ambient_temperature > 30.0:
                    return 1.0
                else:
                    if pollutant == self.pollutant_CO:
                        return 1.9 - 0.03 * ambient_temperature
                    elif pollutant == self.pollutant_NOx:
                        return 1.3 - 0.013 * ambient_temperature
                    elif pollutant == self.pollutant_VOC:
                        return 3.1 - 0.09 * ambient_temperature
                    elif pollutant == self.pollutant_PM:
                        return 3.1 - 0.1 * ambient_temperature
                    elif pollutant == self.pollutant_FC:
                        return 1.34 - 0.008 * ambient_temperature
                    else:
                        raise Exception, "There is no formula to " \
                            "calculate the cold start emission quotient "\
                            "for diesel passenger cars or light " \
                            "commercial vehicles for HC or PM."
        else:
            raise Exception, "There is only formula to calculate cold-start "\
                "emission for passenger cars or light commercial vehicles."


    # Definition of the cold mileage percentage: the "Beta parameter".
    def ColdStartMileagePercentage(self, vehicle_type, engine_type, pollutant,
                         copert_class, engine_capacity, ambient_temperature,
                         avg_trip_length, **kwargs):
        if (vehicle_type == self.vehicle_type_passenger_car or \
            vehicle_type == self.vehicle_type_light_commercial_vehicle) \
            and engine_type == self.engine_type_gasoline:
            if copert_class <= self.class_Euro_1:
                return 0.6474 - 0.02545 * avg_trip_length \
                    - (0.00974 - 0.000385 * avg_trip_length) \
                    * ambient_temperature
            elif copert_class > self.class_Euro_1 \
            and copert_class <= self.class_Euro_4:
                if pollutant == self.pollutant_PM \
                   or pollutant == self.pollutant_FC \
                   or pollutant == self.pollutant_HC:
                    raise Exception, "For gasoline passenger cars with " \
                        "emission standard from Euro 2 to Euro 4, there "\
                        "is no formula for HC, PM and FC to calculate " \
                        "the cold mileage percentage."
                else:
                    beta_euro_1 = self.ColdStartMileagePercentage(vehicle_type,
                                                        engine_type,
                                                        pollutant,
                                                        self.class_Euro_1,
                                                        engine_capacity,
                                                        ambient_temperature,
                                                        avg_trip_length)
                    if copert_class == self.class_Euro_2:
                        if pollutant == self.pollutant_CO:
                            return beta_euro_1 * 0.72
                        elif pollutant == self.pollutant_NOx:
                            return beta_euro_1 * 0.72
                        else:
                            return beta_euro_1 * 0.56
                    elif copert_class == self.class_Euro_3:
                        if pollutant == self.pollutant_CO:
                            return beta_euro_1 * 0.62
                        elif pollutant == self.pollutant_NOx:
                            return beta_euro_1 * 0.32
                        else:
                            return beta_euro_1 * 0.32
                    else:
                        if pollutant == self.pollutant_CO:
                            return beta_euro_1 * 0.18
                        elif pollutant == self.pollutant_NOx:
                            return beta_euro_1 * 0.18
                        else:
                            return beta_euro_1 * 0.18
            else:
                raise Exception, "For gasoline passenger cars with " \
                    "emission standard higher than Euro 5 (included), " \
                    "there is no formula to calculate the beta-"\
                    "parameter."
        elif (vehicle_type == self.vehicle_type_passenger_car \
        or vehicle_type == self.vehicle_type_light_commercial_vehicle) \
        and engine_type == self.engine_type_diesel:
            if vehicle_type == self.vehicle_type_passenger_car:
                beta_gasoline_euro_1 \
                    = self.ColdStartMileagePercentage(vehicle_type,
                                                      self.engine_type_gasoline,
                                                      pollutant,
                                                      self.class_Euro_1,
                                                      engine_capacity,
                                                      ambient_temperature,
                                                      avg_trip_length)
                if copert_class <= self.class_Euro_4:
                    return beta_gasoline_euro_1
                elif copert_class <= self.class_Euro_6:
                    if pollutant == self.pollutant_HC \
                       or pollutant == self.pollutant_FC:
                        raise Exception, "For diesel passenger cars, there " \
                            "is no formula to calculate the beta parameter " \
                            "for HC or FC."
                    else:
                        if pollutant == self.pollutant_NOx:
                            if copert_class == self.class_Euro_5:
                                return (1 - (-0.23)) * beta_gasoline_euro_1
                            else:
                                return (1 - 0.57) * beta_gasoline_euro_1
                        elif pollutant == self.pollutant_PM:
                            if copert_class == self.class_Euro_5:
                                return (1 - 0.95) * beta_gasoline_euro_1
                            else:
                                return (1 - 0.95) * beta_gasoline_euro_1
                        else:
                            return beta_gasoline_euro_1
                else:
                    raise Exception, "For diesel passenger cars with " \
                        "emission standard of Euro 6c, there " \
                        "is no formula to calculate the beta parameter."

            else:
                beta_diesel_passenger \
                    = self.ColdStartMileagePercentage(self.vehicle_type_passenger_car,
                                                      self.engine_type_diesel,
                                                      pollutant,
                                                      copert_class,
                                                      engine_capacity,
                                                      ambient_temperature,
                                                      avg_trip_length)
                if copert_class <= self.class_Euro_2:
                    return beta_diesel_passenger
                else:
                    if pollutant == self.pollutant_HC \
                       or pollutant == self.pollutant_FC:
                        raise Exception, "For diesel light commercial cars, "\
                            "there is no formula to calculate the beta-" \
                            "parameter for HC and FC."
                    else:
                        if copert_class == self.class_Euro_3:
                            if pollutant == self.pollutant_CO:
                                return (1 - 0.18) * beta_diesel_passenger
                            elif pollutant == self.pollutant_NOx:
                                return (1 - 0.16) * beta_diesel_passenger
                            elif pollutant == self.pollutant_VOC:
                                return (1 - 0.38) * beta_diesel_passenger
                            else:
                                return (1 - 0.33) * beta_diesel_passenger
                        elif copert_class == self.class_Euro_4:
                            if pollutant == self.pollutant_CO:
                                return (1 - 0.35) * beta_diesel_passenger
                            elif pollutant == self.pollutant_NOx:
                                return (1 - 0.32) * beta_diesel_passenger
                            elif pollutant == self.pollutant_VOC:
                                return (1 - 0.77) * beta_diesel_passenger
                            else:
                                return (1 - 0.65) * beta_diesel_passenger
                        else:
                            raise Exception, "For diesel passenger cars " \
                                "with emission standard higher than Euro 5" \
                                "(included), there is no formula to "\
                                "calculate the beta-parameter."
        else:
            raise Exception, "There are only formula for gasoline and " \
                "diesel passenger cars or light commercial cars to " \
                "calculate the beta-parameter for cold-start emissions."


    # Definition of Hot Emission Factor (HEF) for diesel passenger cars.
    def HEFDieselPassengerCar(self, pollutant, speed, copert_class,
                              engine_capacity, **kwargs):
        """Computes the hot emissions factor in g/km for diesel passenger
        cars, except for fuel consumption-dependent emissions
        (SO2,Pb,heavy metals).

        @param pollutant The pollutant for which the emissions are
        computed. It can be any of Copert.pollutant_*.

        @param speed The average velocity of the vehicles in kilometers per
        hour.

        @param copert_class The vehicle class, which can be any of the
        Copert.class_* attributes. They are introduced in the EMEP/EEA
        emission inventory guidebook.

        @param engine_capacity The engine capacity in liter.
        """

        # Global indexes of EURO classes, ordered by appearance in the
        # guidebook.
        global_class_index = [self.class_Euro_1, self.class_Euro_2,
                              self.class_Euro_3, self.class_Euro_4]

        if copert_class == self.class_Euro_3_GDI:
            raise Exception, "Class Euro_3_GDI has no hot emission factor " \
                + "formula in case of diesel cars."

        V = speed
        if V < 10. or V > 130.:
            raise Exception, "There is no formula to calculate hot " \
                "emission factors for diesel passenger cars when the speed " \
                "is lower than 10 km/h or higher than 130 km/h."
        else:
            if copert_class < self.class_Euro_1: # Pre-Euro
                if pollutant == self.pollutant_CO:
                    return self.power(5.41301, -0.574, V)
                elif pollutant == self.pollutant_NOx:
                    if engine_capacity <= 2.0:
                        return self.quadratic(0.000101, -0.014, 0.918, V)
                    else:
                        return self.quadratic(0.000133, -0.018, 1.331, V)
                elif pollutant == self.pollutant_VOC:
                    return self.power(4.61, -0.937, V)
                elif pollutant == self.pollutant_PM:
                    return self.quadratic(0.000058, -0.0086, 0.45, V)
                elif pollutant == self.pollutant_FC:
                    return self.quadratic(0.014, -2.084, 118.489, V)
            else:
                if copert_class <= self.class_Euro_4:
                    copert_index = global_class_index.index(copert_class)
                    if engine_capacity < 1.4:
                        a, b, c, d, e, f = self.efc_diesel_passenger_car\
                                           [pollutant][copert_index]\
                                           [self.engine_capacity_less_1p4]
                        if math.isnan(a) and copert_class <= self.class_Euro_3:
                            raise Exception, "There is no formula to " \
                                "calculate hot emission factors of " \
                                + self.name_pollutant[pollutant] + ", for "\
                                + "diesel passenger cars of copert class " \
                                + self.name_class_euro[copert_class] + ", "\
                                + "with an engine capacity lower than 1.4 l."
                    elif engine_capacity < 2.0:
                        a, b, c, d, e, f = self.efc_diesel_passenger_car\
                                           [pollutant][copert_index]\
                                           [self.engine_capacity_1p4_to_2]
                    else:
                        a, b, c, d, e, f = self.efc_diesel_passenger_car\
                                           [pollutant][copert_index]\
                                           [self.engine_capacity_more_2]
                    if pollutant == self.pollutant_CO \
                       and copert_class == self.class_Euro_4:
                        return 17.5e-3 + 86.42 \
                            * (1 + math.exp(-(V + 117.67) / (-21.99)))**(-1)
                    else:
                        return self.EF_30(a, b, c, d, e, f, V)
                else:
                    if engine_capacity < 1.4:
                        i_engine = 4
                    elif engine_capacity >= 1.4 and engine_capacity < 2.0:
                        i_engine = 5
                    else:
                        i_engine = 6
                    i_copert_class = self.index_copert_class_pc[copert_class]
                    if pollutant == self.pollutant_VOC \
                       or pollutant == self.pollutant_FC:
                        raise Exception, "There is no formula to calculate " \
                            "hot emission factors of VOC and FC for " \
                            "gasoline passenger cars of emission standard " \
                            "higher than Euro 5 (included)."
                    else:
                        i_pollutant = self.index_pollutant[pollutant]
                    a, b, c, d, e, f, g, h, rf, Vmin, Vmax, N_eq \
                        = self.pc_parameter[i_engine, i_copert_class,
                                            i_pollutant]
                    if V < Vmin or V > Vmax:
                        raise Exception, "The input speed must be in the  " \
                            + "range of [" + str(round(Vmin, 1)) + ", " \
                            + str(round(Vmax, 1)) + "] when calculating " \
                            "hot emission factors for passenger cars " \
                            "with emission standard of Euro 5 or higher."
                    emission_factor \
                        = self.list_equation_pc_ldv[int(N_eq)](self, a, b, c,
                                                               d, e, f, g, h,
                                                               rf, V)
                    return emission_factor


    # Definition of Hot Emission Factor (HEF) for light commercial vehicles.
    def HEFLightCommercialVehicle(self, pollutant, speed, engine_type,
                                  copert_class, **kwargs):
        V = speed
        if V == 0.0:
            return 0.0
        else:
            index_pollutant_pre_euro_4 = {self.pollutant_CO: 0,
                                          self.pollutant_NOx: 1,
                                          self.pollutant_VOC: 2,
                                          self.pollutant_PM: 3,
                                          self.pollutant_FC: 4}
            if copert_class <= self.class_Euro_1:
                index_copert_class = {self.class_Improved_Conventional: 0,
                                      self.class_Euro_1: 1}
                i_copert_class = index_copert_class[copert_class]
                i_pollutant = index_pollutant_pre_euro_4[pollutant]
                if engine_type == self.engine_type_gasoline \
                   and (pollutant == self.pollutant_PM \
                        or pollutant == self.pollutant_HC):
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factors for PM and HC when engine type " \
                        "is gasoline, with emission standard of " \
                        "Conventional or Euro 1."
                if engine_type == self.engine_type_diesel \
                   and pollutant == self.pollutant_HC:
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factors for HC when engine type is " \
                        "diesel, with emission standard of Conventional " \
                        "or Euro 1."
                else:
                    Vmin, Vmax, a, b, c \
                           = self.ldv_parameter_pre_euro_1[engine_type,
                                                           i_pollutant,
                                                           i_copert_class,:]
                    if V < Vmin or V > Vmax:
                        raise Exception, "The input speed must be in the " \
                            + "range of [" + str(round(Vmin, 1)) + ", " \
                            + str(round(Vmax, 1)) + "] when calculating " \
                            "hot emission factors for light commercial " \
                            "vehicles, with emission standard of " \
                            "Conventional or Euro 1."
                    else:
                        return self.quadratic(a, b, c, V)
            if copert_class >= self.class_Euro_2 \
               and copert_class <= self.class_Euro_4:
                emission_factor_euro_1 \
                    = self.HEFLightCommercialVehicle(pollutant, V,
                                                     engine_type,
                                                     self.class_Euro_1)
                if pollutant != self.pollutant_HC \
                   and pollutant != self.pollutant_FC:
                    i_engine_type = engine_type
                    i_pollutant = index_pollutant_pre_euro_4[pollutant]
                    index_copert_class = {self.class_Euro_2: 0,
                                          self.class_Euro_3: 1,
                                          self.class_Euro_4: 2}
                    i_copert_class = index_copert_class[copert_class]
                    reduction_percentage \
                        = 0.01 * self.ldv_reduction_percentage[i_engine_type,
                                                               i_copert_class,
                                                               i_pollutant]
                    return emission_factor_euro_1 \
                        * (1.0 - reduction_percentage)
                else:
                    raise Exception, "There is no formula to calculate hot " \
                        "emission factors for the requested pollutant when " \
                        "emission standard is between Euro 2 and Euro 4."
                    return None
            elif copert_class >= self.class_Euro_5:
                i_pollutant = self.index_pollutant[pollutant]
                i_copert_class = self.index_copert_class_ldv[copert_class]
                a, b, c, d, e, f, g, h, rf, Vmin, Vmax, N_eq \
                    = self.ldv_parameter[engine_type, i_copert_class,
                                         i_pollutant]
                if V < Vmin or V > Vmax:
                    raise Exception, "The input speed must be in the " \
                        + "range of [" + str(round(Vmin, 1)) + ", " \
                        + str(round(Vmax, 1)) + "] when calculating hot " \
                        "emission factors for light commercial vehicles, " \
                        "with emission standard of Euro 5 or higher."
                emission_factor \
                    = self.list_equation_pc_ldv[int(N_eq)](self, a, b, c, d,
                                                           e, f, g, h, rf, V)
                return emission_factor


    # Definition of Hot Emission Factor (HEF) for heavy duty vehicles and
    # buses.
    def HEFHeavyDutyVehicle(self, speed, vehicle_category, hdv_type,
                            hdv_copert_class, pollutant,
                            load, slope, **kwargs):
        V = speed
        name_hdv_type \
            = self.corr_hdv_type.keys()[self.corr_hdv_type.values().index(hdv_type)]
        name_slope \
            = self.corr_slope.keys()[self.corr_slope.values().index(slope)]
        name_load \
            = self.corr_load.keys()[self.corr_load.values().index(load)]
        i_hdv_or_bus = self.index_vehicle_type[vehicle_category]
        i_hdv_type = hdv_type
        i_hdv_copert_class = hdv_copert_class
        i_pollutant = self.index_pollutant[pollutant]
        i_load = load
        i_slope = slope
        a, b, c, d, e, f, g, Vmin, Vmax, N_eq \
            = self.hdv_parameter[i_hdv_or_bus, hdv_type, i_hdv_copert_class,
                                 i_pollutant, i_load, i_slope]
        if N_eq >= 0:
            if V < Vmin or V > Vmax:
                raise Exception, "The input speed must be in the " \
                    + "range of [" + str(round(Vmin, 1)) + ", " \
                    + str(round(Vmax, 1)) + "] when calculating hot " \
                    "emission factors for heavy duty vehicles of type " \
                    + name_hdv_type + " when the charge is " + name_load \
                    + "% and the slope is " + name_slope + "."
            emission_factor = self.list_equation_hdv[int(N_eq)](self, a, b, c,
                                                                d, e, f, g, V)
        else:
            raise Exception, "There is no formula available for the " \
                " requested vehicle technology or/and pollutant."
        return emission_factor


    # Definition of Emission Factor (EF) for mopeds. There is no distinction
    # between hot and cold-start emissions, and only the emission factors
    # under urban driving conditions are given.
    def EFMoped(self, pollutant, speed, engine_type, copert_class, **kwargs):
        if copert_class in [self.class_Improved_Conventional,
                            self.class_Euro_1, self.class_Euro_2,
                            self.class_Euro_3] \
            and pollutant != self.pollutant_HC:
            i_copert_class = self.index_copert_class_moto[copert_class]
            index_pollutant = {self.pollutant_CO: 0, self.pollutant_NOx: 1,
                               self.pollutant_VOC: 2, self.pollutant_FC: 3,
                               self.pollutant_PM: 4}
            i_pollutant = index_pollutant[pollutant]
            if engine_type == self.engine_type_two_stroke_less_50:
                return self.moped_parameter[0, i_copert_class, i_pollutant]
            elif engine_type == self.engine_type_four_stroke_less_50:
                return self.moped_parameter[1, i_copert_class, i_pollutant]
        else:
            raise Exception, "Only formulas for mopeds with emission " \
                "standard of Conventional, Euro 1 - Euro 3 are available, " \
                "and there is no formula for the pollutant HC."

    # Definition of Emission Factor (EF) for motorcycles.
    def EFMotorcycle(self, pollutant, speed, engine_type, copert_class,
                     **kwargs):
        V = speed
        if copert_class in [self.class_Improved_Conventional,
                            self.class_Euro_1, self.class_Euro_2,
                            self.class_Euro_3] \
            and pollutant != self.pollutant_VOC:
            i_engine_type = self.index_moto_engine_type[engine_type]
            name_engine_type \
                = self.corr_engine_type.keys()[self.corr_engine_type.values().index(engine_type)]
            i_pollutant = self.index_pollutant[pollutant]
            i_copert_class = self.index_copert_class_moto[copert_class]
            Vmin, Vmax, a5, a4, a3, a2, a1, a0 \
                = self.moto_parameter[i_engine_type, i_pollutant,
                                      i_copert_class]
            if V < Vmin or V > Vmax:
                raise Exception, "The input speed must be in the " \
                    + "range of [" + str(round(Vmin, 1)) + ", " \
                    + str(round(Vmax, 1)) + "] when calculating " \
                    "emission factors for motorcycles when engine type is " \
                    + name_engine_type + "."
            else:
                return self.Eq_56(a0, a1, a2, a3, a4, a5, V)
        else:
            raise Exception, "Only formulas for motorcycles with emission " \
                "standard of Conventional, Euro 1 - Euro 3 are available, " \
                "and there is no formula for the pollutant VOC."
