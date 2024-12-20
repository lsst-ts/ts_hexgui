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

__all__ = ["Config"]

from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class to have the configuration details."""

    # In micron / sec^2
    strut_acceleration_limit: float = 0.0

    # In micron / sec
    hexapod_linear_radial_velocity_max: float = 0.0
    hexapod_linear_axial_velocity_max: float = 0.0

    # In deg / sec
    hexapod_angular_radial_velocity_max: float = 0.0
    hexapod_angular_axial_velocity_max: float = 0.0

    # In micron
    strut_upper_position_max: float = 0.0

    # In micron / sec
    strut_velocity_max: float = 0.0

    # In micron
    hexapod_position_xy_max: float = 0.0
    hexapod_position_z_min: float = 0.0
    hexapod_position_z_max: float = 0.0

    # In degree
    hexapod_position_rxry_max: float = 0.0
    hexapod_position_rz_min: float = 0.0
    hexapod_position_rz_max: float = 0.0

    # In micron
    hexapod_pivot: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    drives_enabled: bool = False
