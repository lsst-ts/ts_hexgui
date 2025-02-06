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

__all__ = ["MockController"]

import logging
import typing

import numpy as np
from lsst.ts.hexrotcomm import BaseMockController, Command
from lsst.ts.xml.enums import MTHexapod

from .constants import (
    CAM_UV_MAX_DEG,
    CAM_W_MAX_DEG,
    CAM_W_MIN_DEG,
    CAM_XY_MAX_MIC,
    CAM_Z_MAX_MIC,
    CAM_Z_MIN_MIC,
    M2_UV_MAX_DEG,
    M2_W_MAX_DEG,
    M2_W_MIN_DEG,
    M2_XY_MAX_MIC,
    M2_Z_MAX_MIC,
    M2_Z_MIN_MIC,
    MAX_ACCEL_LIMIT,
    MAX_ACTUATOR_RANGE_MIC,
    MAX_ANGULAR_VEL_LIMIT,
    MAX_LINEAR_VEL_LIMIT,
    NUM_DEGREE_OF_FREEDOM,
    NUM_DRIVE,
    NUM_STRUT,
)
from .enums import CommandCode
from .structs import Config, Telemetry


class MockController(BaseMockController):
    """Mock controller to simulate the controller behavior.

    Parameters
    ----------
    log : `logging.Logger`
        Logger.
    hexapod_type : enum `MTHexapod.SalIndex`
        The hexapod type.
    port : `int`, optional
        Command socket port. (the default is 0)
    initial_state : enum `MTHexapod.ControllerState`, optional
        Initial state of the mock controller.
    """

    # Strut current (A) and bus voltage (V) as constants
    STRUT_CURRENT = 0.8
    BUS_VOLTAGE = 330.0

    # Strut speed (um/sec)
    STRUT_SPEED = 500.0

    # Pivot position x, y, and z (um)
    PIVOT = (0.0, 0.0, -703000.0)

    # Move position "um" and "deg" per cycle
    CYCLE_MOVE_POSITION_UM = 100
    CYCLE_MOVE_POSITION_DEG = 0.01

    def __init__(
        self,
        log: logging.Logger,
        hexapod_type: MTHexapod.SalIndex,
        port: int = 0,
        initial_state: MTHexapod.ControllerState = MTHexapod.ControllerState.STANDBY,
    ) -> None:

        extra_commands = {
            (
                CommandCode.SET_ENABLED_SUBSTATE,
                1,  # Move in the controller
            ): self.do_move_point_to_point,
            (
                CommandCode.SET_ENABLED_SUBSTATE,
                3,  # Stop in the controller
            ): self.do_stop,
            CommandCode.POSITION_SET: self.do_position_set,
            CommandCode.POSITION_OFFSET: self.do_position_offset,
            CommandCode.SET_RAW_STRUT: self.do_set_raw_strut,
            CommandCode.SET_PIVOT_POINT: self.do_set_pivot_point,
            CommandCode.MASK_LIMIT_SW: self.do_mask_limit_switch,
            CommandCode.CMD_SOURCE: self.do_switch_command_source,
            CommandCode.CONFIG_ACCEL: self.do_config_accel,
            CommandCode.CONFIG_VEL: self.do_config_vel,
        }

        super().__init__(
            log=log,
            CommandCode=CommandCode,
            extra_commands=extra_commands,
            config=self._create_config(hexapod_type),
            telemetry=self._create_telemetry(),
            port=port,
            initial_state=initial_state,
        )

        # Whether the CSC is the commander
        self._is_csc_commander = False

        # Commanded hexapod position (x, y, z, u, v, w) in microns and degrees.
        # If None, no position has been commanded.
        self._commanded_position: list[float] | None = None

    def _create_config(self, hexapod_type: MTHexapod.SalIndex) -> Config:
        """Create the configuration.

        Parameters
        ----------
        hexapod_type : enum `MTHexapod.SalIndex`
            The hexapod type.

        Returns
        -------
        config : `Config`
            Configuration.
        """

        config = Config()
        config.acceleration_strut = MAX_ACCEL_LIMIT

        config.vel_limits = (
            MAX_LINEAR_VEL_LIMIT,
            MAX_LINEAR_VEL_LIMIT,
            MAX_ANGULAR_VEL_LIMIT,
            MAX_ANGULAR_VEL_LIMIT,
        )

        config.max_displacement_strut = MAX_ACTUATOR_RANGE_MIC
        config.max_velocity_strut = self.STRUT_SPEED

        config.pos_limits = (
            (
                CAM_XY_MAX_MIC,
                CAM_Z_MIN_MIC,
                CAM_Z_MAX_MIC,
                CAM_UV_MAX_DEG,
                CAM_W_MIN_DEG,
                CAM_W_MAX_DEG,
            )
            if hexapod_type == MTHexapod.SalIndex.CAMERA_HEXAPOD
            else (
                M2_XY_MAX_MIC,
                M2_Z_MIN_MIC,
                M2_Z_MAX_MIC,
                M2_UV_MAX_DEG,
                M2_W_MIN_DEG,
                M2_W_MAX_DEG,
            )
        )

        config.pivot = self.PIVOT

        config.drives_enabled = False

        return config

    def _create_telemetry(self) -> Telemetry:
        """Create the telemetry.

        Returns
        -------
        telemetry : `Telemetry`
            Telemetry.
        """

        telemetry = Telemetry()
        telemetry.bus_voltage = (self.BUS_VOLTAGE,) * NUM_DRIVE

        return telemetry

    async def do_move_point_to_point(self, command: Command) -> None:
        """Do the point-to-point movement.

        Parameters
        ----------
        command : `Command`
            Command.

        Raises
        ------
        `RuntimeError`
            When the position or offset is not set.
        """

        self.assert_stationary()

        if self._commanded_position is None:
            raise RuntimeError("Must set the position or offset first.")

        self.telemetry.commanded_pos = tuple(self._commanded_position)
        self.telemetry.strut_commanded_final_pos = (
            self._hexapod_position_to_strut_position(self._commanded_position)
        )
        self.telemetry.strut_commanded_accel = (
            self.config.acceleration_strut,
        ) * NUM_STRUT

        self.telemetry.enabled_substate = (
            MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT
        )

    def _hexapod_position_to_strut_position(
        self,
        hexapod_position: tuple[float, float, float, float, float, float] | list[float],
    ) -> tuple[float, float, float, float, float, float]:
        """Hexapod position to the strut position.

        Notes
        -----
        The calculation here is just a simple transformation of the hexapod
        position to the strut position.

        Parameters
        ----------
        hexapod_position : `tuple` or `list`
            Hexapod position (x, y, z, u, v, w) in microns and degrees.

        Returns
        -------
        `tuple`
            Six strut positions in meter.
        """

        UM_TO_M = 1e-6
        strut_position_x = hexapod_position[0] * UM_TO_M
        strut_position_y = hexapod_position[1] * UM_TO_M
        strut_position_z = hexapod_position[2] * np.sqrt(3) * UM_TO_M

        # Just a random scale factor
        DEG_TO_M_SCALE_FACTOR = 1e-3
        strut_position_rx = hexapod_position[3] * DEG_TO_M_SCALE_FACTOR
        strut_position_ry = hexapod_position[4] * DEG_TO_M_SCALE_FACTOR
        strut_position_rz = hexapod_position[5] * DEG_TO_M_SCALE_FACTOR

        return (
            strut_position_z + strut_position_rz + strut_position_x + strut_position_ry,
            strut_position_z + strut_position_rz + strut_position_y + strut_position_rx,
            strut_position_z + strut_position_rz + strut_position_x + strut_position_ry,
            strut_position_z + strut_position_rz + strut_position_y + strut_position_rx,
            strut_position_z + strut_position_rz + strut_position_x + strut_position_ry,
            strut_position_z + strut_position_rz + strut_position_y + strut_position_rx,
        )

    async def do_stop(self, command: Command) -> None:
        """Stop the movement.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.telemetry.enabled_substate = MTHexapod.EnabledSubstate.STATIONARY

    async def do_position_set(self, command: Command) -> None:
        """Set the position.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._commanded_position = [
            getattr(command, f"param{idx + 1}") for idx in range(NUM_DEGREE_OF_FREEDOM)
        ]

    async def do_position_offset(self, command: Command) -> None:
        """Set the position offset.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        current_positions = list(self.telemetry.measured_xyz) + list(
            self.telemetry.measured_uvw
        )
        offsets = [
            getattr(command, f"param{idx + 1}") for idx in range(NUM_DEGREE_OF_FREEDOM)
        ]
        self._commanded_position = [
            position + offset for position, offset in zip(current_positions, offsets)
        ]

    async def do_set_raw_strut(self, command: Command) -> None:
        """Set the raw strut position.

        Parameters
        ----------
        command : `Command`
            Command.

        Raises
        ------
        `RuntimeError`
            Not supported in the simulator.
        """

        raise RuntimeError("Not supported in the simulator.")

    async def do_set_pivot_point(self, command: Command) -> None:
        """Set the pivot point.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self.config.pivot = (command.param1, command.param2, command.param3)
        await self.write_config()

    async def do_mask_limit_switch(self, command: Command) -> None:
        """Mask the limit switch.

        Parameters
        ----------
        command : `Command`
            Command.

        Raises
        ------
        `RuntimeError`
            Not supported in the simulator.
        """

        raise RuntimeError("Not supported in the simulator.")

    async def do_switch_command_source(self, command: Command) -> None:
        """Switch the command source.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self._is_csc_commander = command.param1 == 1.0

    async def do_config_accel(self, command: Command) -> None:
        """Configure the acceleration.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "acceleration", MAX_ACCEL_LIMIT)

        self.config.acceleration_strut = command.param1
        await self.write_config()

    def _check_positive_value(self, value: float, name: str, max_value: float) -> None:
        """Check that a numeric value is in range.

        Parameters
        ----------
        value : `float`
            Value to check.
        name : `str`
            Name of value.
        max_value : `float`
            Maximum allowed value of the named field (inclusive).

        Raises
        ------
        `RuntimeError`
            When the value is not in range.
        """

        if not 0 < value <= max_value:
            raise RuntimeError(f"{name}={value} not in range (0, {max_value}]")

    async def do_config_vel(self, command: Command) -> None:
        """Configure the velocity.

        Parameters
        ----------
        command : `Command`
            Command.
        """

        self.assert_stationary()

        self._check_positive_value(command.param1, "xy", MAX_LINEAR_VEL_LIMIT)
        self._check_positive_value(command.param2, "uv", MAX_ANGULAR_VEL_LIMIT)
        self._check_positive_value(command.param3, "z", MAX_LINEAR_VEL_LIMIT)
        self._check_positive_value(command.param4, "w", MAX_ANGULAR_VEL_LIMIT)

        self.config.vel_limits = (
            command.param1,
            command.param3,
            command.param2,
            command.param4,
        )
        await self.write_config()

    async def end_run_command(
        self, command: Command, cmd_method: typing.Coroutine
    ) -> None:

        if cmd_method not in (self.do_position_set, self.do_position_offset):
            self._commanded_position = None

    async def update_telemetry(self, curr_tai: float) -> None:
        try:
            # Copley drive status
            self.telemetry.latching_fault_status_register = (0,) * NUM_STRUT
            self.telemetry.input_pin_states = (0x380E0,) * NUM_DRIVE

            self.telemetry.copley_fault_status_register = (0xF000,) * NUM_STRUT

            self.telemetry.status_word = (
                (0x631,) * NUM_STRUT
                if self.config.drives_enabled
                else (0x670,) * NUM_STRUT
            )

            # Application status
            self.telemetry.application_status = (
                MTHexapod.ApplicationStatus.EUI_CONNECTED
                | MTHexapod.ApplicationStatus.SYNC_MODE
            )
            if self._is_csc_commander:
                self.telemetry.application_status |= (
                    MTHexapod.ApplicationStatus.DDS_COMMAND_SOURCE
                )

            # Power
            self.telemetry.motor_current = (
                (self.STRUT_CURRENT,) * NUM_STRUT
                if self.config.drives_enabled
                else (0.0,) * NUM_STRUT
            )
            self.telemetry.bus_voltage = (self.BUS_VOLTAGE,) * NUM_DRIVE

            # Hexapod and strut positions
            if (
                self.telemetry.enabled_substate
                == MTHexapod.EnabledSubstate.MOVING_POINT_TO_POINT
            ):
                # Do the movement
                is_done_x, new_x = self._move_position(
                    self.telemetry.measured_xyz[0],
                    self.telemetry.commanded_pos[0],
                    self.CYCLE_MOVE_POSITION_UM,
                )
                is_done_y, new_y = self._move_position(
                    self.telemetry.measured_xyz[1],
                    self.telemetry.commanded_pos[1],
                    self.CYCLE_MOVE_POSITION_UM,
                )
                is_done_z, new_z = self._move_position(
                    self.telemetry.measured_xyz[2],
                    self.telemetry.commanded_pos[2],
                    self.CYCLE_MOVE_POSITION_UM,
                )

                is_done_u, new_u = self._move_position(
                    self.telemetry.measured_uvw[0],
                    self.telemetry.commanded_pos[3],
                    self.CYCLE_MOVE_POSITION_DEG,
                )
                is_done_v, new_v = self._move_position(
                    self.telemetry.measured_uvw[1],
                    self.telemetry.commanded_pos[4],
                    self.CYCLE_MOVE_POSITION_DEG,
                )
                is_done_w, new_w = self._move_position(
                    self.telemetry.measured_uvw[2],
                    self.telemetry.commanded_pos[5],
                    self.CYCLE_MOVE_POSITION_DEG,
                )

                # Set the new hexapod position
                self.telemetry.measured_xyz = (new_x, new_y, new_z)
                self.telemetry.measured_uvw = (new_u, new_v, new_w)

                # Set the new strut position
                strut_positions = self._hexapod_position_to_strut_position(
                    tuple(self.telemetry.measured_xyz)  # type: ignore[arg-type]
                    + tuple(self.telemetry.measured_uvw)
                )

                M_TO_UM = 1e6
                for idx, strut_position in enumerate(strut_positions):
                    self.telemetry.estimated_posfiltvel[idx].pos = (
                        strut_position * M_TO_UM
                    )

                # Change the substate if the movement is done
                if (
                    is_done_x
                    and is_done_y
                    and is_done_z
                    and is_done_u
                    and is_done_v
                    and is_done_w
                ):
                    self.telemetry.enabled_substate = (
                        MTHexapod.EnabledSubstate.STATIONARY
                    )

                    self._commanded_position = None
                # Update the Copley drive status word
                else:
                    status_word_current = tuple(self.telemetry.status_word)
                    # 0x4000 is bit 14 (Amplifier move status)
                    self.telemetry.status_word = tuple(
                        word | 0x4000 for word in status_word_current
                    )

        except Exception:
            self.log.exception("update_telemetry failed; output incomplete telemetry")

    def _move_position(
        self, position_current: float, position_target: float, step: float
    ) -> tuple[bool, float]:
        """Move the position.

        Parameters
        ----------
        position_current : `float`
            Current position.
        position_target : `float`
            Target position.
        step : `float`
            Step. Should be a positive value.

        Returns
        -------
        `tuple` [`bool`, `float`]
            Whether the movement is done and the new position. True if the
            movement is done. False otherwise.
        """

        # Return if the current position is already at the target position
        if position_current == position_target:
            return (True, position_current)

        # Determine the direction to move and calculate the new position
        direction = np.sign(position_target - position_current)
        position_new = position_current + direction * step

        # Check if the new position is at the target position
        if (direction > 0) and (position_new >= position_target):
            return (True, position_target)

        if (direction < 0) and (position_new <= position_target):
            return (True, position_target)

        # Return the new position
        return (False, position_new)
