# This file is part of ts_hexgui.
#
# Developed for the Vera Rubin Observatory Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = [
    "NUM_STRUT",
    "NUM_DRIVE",
    "NUM_DEGREE_OF_FREEDOM",
    "MAX_ACTUATOR_RANGE_MIC",
    "MAX_ACCEL_LIMIT",
    "MAX_LINEAR_VEL_LIMIT",
    "MAX_ANGULAR_VEL_LIMIT",
    "CAM_XY_MAX_MIC",
    "CAM_Z_MIN_MIC",
    "CAM_Z_MAX_MIC",
    "CAM_UV_MAX_DEG",
    "CAM_W_MIN_DEG",
    "CAM_W_MAX_DEG",
    "M2_XY_MAX_MIC",
    "M2_Z_MIN_MIC",
    "M2_Z_MAX_MIC",
    "M2_UV_MAX_DEG",
    "M2_W_MIN_DEG",
    "M2_W_MAX_DEG",
    "MAX_PIVOT_X_MIC",
    "MAX_PIVOT_Y_MIC",
    "MAX_PIVOT_Z_MIC",
]


# Number of the struts
NUM_STRUT = 6

# Number of the drives
NUM_DRIVE = 3

# Number of the degree of freedom
NUM_DEGREE_OF_FREEDOM = 6

# Limit of the actuator linear range
MAX_ACTUATOR_RANGE_MIC = 14100.0

# For the following limits, see ts_hexapod_controller.

# Limit for the strut acceleration (um/sec^2).
MAX_ACCEL_LIMIT = 500.0

# Limits for the hexapod velocity (um/sec or deg/sec).
MAX_LINEAR_VEL_LIMIT = 2000.0
MAX_ANGULAR_VEL_LIMIT = 0.1146

# Position limits of the camera hexapod
CAM_XY_MAX_MIC = 11400.0
CAM_Z_MIN_MIC = -13100.0
CAM_Z_MAX_MIC = 13100.0
CAM_UV_MAX_DEG = 0.36
CAM_W_MIN_DEG = -0.1
CAM_W_MAX_DEG = 0.1

# Position limits of the M2 hexapod
M2_XY_MAX_MIC = 10500.0
M2_Z_MIN_MIC = -8900.0
M2_Z_MAX_MIC = 8900.0
M2_UV_MAX_DEG = 0.175
M2_W_MIN_DEG = -0.05
M2_W_MAX_DEG = 0.05

# Limits of the pivot
MAX_PIVOT_X_MIC = 500000.0
MAX_PIVOT_Y_MIC = 500000.0
MAX_PIVOT_Z_MIC = 3500000.0
