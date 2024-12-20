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
    "SignalState",
    "SignalApplicationStatus",
    "SignalPosition",
    "SignalPower",
    "SignalControl",
    "SignalDrive",
    "SignalConfig",
]

from PySide6 import QtCore


class SignalState(QtCore.QObject):
    """State signal to send the current controller's state."""

    # Command source, enum of `CommandSource`
    command_source = QtCore.Signal(int)

    # Controller's state, enum of `lsst.ts.xml.enums.MTHexapod.ControllerState`
    state = QtCore.Signal(int)

    # Enabled substate, enum of `lsst.ts.xml.enums.MTHexapod.EnabledSubstate`
    substate_enabled = QtCore.Signal(int)


class SignalApplicationStatus(QtCore.QObject):
    """Application-status signal to send the current application status."""

    # Application status
    status = QtCore.Signal(int)


class SignalPosition(QtCore.QObject):
    """Position signal to send the current position of hexapod."""

    # Strut positions of [strut_0, strut_1, ..., strut_5] in micron
    strut_position = QtCore.Signal(object)

    # Strut position errors of [strut_0, strut_1, ..., strut_5] in micron
    strut_position_error = QtCore.Signal(object)

    # Hexapod positions of [x, y, z, rx, ry, rz] in micron and degree
    hexapod_position = QtCore.Signal(object)

    # Hexapod is in motion or not
    in_motion = QtCore.Signal(bool)


class SignalPower(QtCore.QObject):
    """Power signal to send the current current and voltage."""

    # Currents of [strut_0, strut_1, ..., strut_5] in ampere
    current = QtCore.Signal(object)

    # Bus voltages of [drive_0, drive_1, drive_2] in volts
    voltage = QtCore.Signal(object)


class SignalControl(QtCore.QObject):
    """Control signal to send the commands of the struts."""

    # Commanded accelerations of [strut_0, strut_1, ..., strut_5] in um/sec^2
    command_acceleration = QtCore.Signal(object)

    # Commanded positions of [strut_0, strut_1, ..., strut_5] in um
    command_position = QtCore.Signal(object)

    # Time frame difference in seconds
    time_difference = QtCore.Signal(float)


class SignalDrive(QtCore.QObject):
    """Drive signal to sent the current drive status."""

    # Status word of [strut_0, strut_1, ..., strut_5]
    status_word = QtCore.Signal(object)

    # Latching fault status of [strut_0, strut_1, ..., strut_5]
    latching_fault = QtCore.Signal(object)

    # Copley drive status of [strut_0, strut_1, ..., strut_5]
    copley_status = QtCore.Signal(object)

    # Input pin status of [strut_0, strut_1, ..., strut_5]
    input_pin = QtCore.Signal(object)


class SignalConfig(QtCore.QObject):
    """Configuration signal to send the current configuration."""

    # Instance of `Config` class
    config = QtCore.Signal(object)
