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

compute = copert.Copert()

print compute.Emission(pollutant = compute.pollutant_CO,
                       speed = 1300.,
                       distance = 1.,
                       vehicle_type = compute.vehicle_type_passenger_car,
                       engine_type = compute.engine_type_gasoline,
                       copert_class = compute.class_ECE_15_00_or_01,
                       engine_capacity = 1.4,
                       ambient_temperature = 20.)
