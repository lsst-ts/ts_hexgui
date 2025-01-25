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

__all__ = ["Model"]

import asyncio
import logging
import typing

from lsst.ts.hexrotcomm import Command, CommandTelemetryClient
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import Signal

from .constants import NUM_DEGREE_OF_FREEDOM, NUM_DRIVE, NUM_STRUT
from .enums import (
    CommandCode,
    CommandSource,
    MotionPattern,
    TriggerEnabledSubState,
    TriggerState,
)
from .signals import (
    SignalApplicationStatus,
    SignalConfig,
    SignalControl,
    SignalDrive,
    SignalPosition,
    SignalPower,
    SignalState,
)
from .status import Status
from .structs import Config, Telemetry


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    hexapod_type : `MTHexapod.SalIndex`
        The hexapod type.
    host : `str`, optional
        Host address. (the default is "localhost")
    port : `int`, optional
        Port to connect. (the default is 5560)
    timeout_connection : `float`, optional
        Connection timeout in second. (the default is 10.0)
    is_simulation_mode : `bool`, optional
        True if running in simulation mode. (the default is False)
    duration_refresh : `int`, optional
        Duration to refresh the data in milliseconds. (the default is 100)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    hexapod_type : `MTHexapod.SalIndex`
        The hexapod type.
    connection_information : `dict`
        TCP/IP connection information.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    signals : `dict`
        Signals to emit the data.
    client : `lsst.ts.hexrotcomm.CommandTelemetryClient` or None
        Command and telemetry client. (the default is None)
    """

    def __init__(
        self,
        log: logging.Logger,
        hexapod_type: MTHexapod.SalIndex,
        host: str = "localhost",
        port: int = 5560,
        timeout_connection: float = 10.0,
        is_simulation_mode: bool = False,
        duration_refresh: int = 100,
    ) -> None:

        self.log = log
        self.hexapod_type = hexapod_type

        self.connection_information = {
            "host": host,
            "port": port,
            "timeout_connection": timeout_connection,
        }

        self._is_simulation_mode = is_simulation_mode
        self.duration_refresh = duration_refresh

        self._status = Status()

        self.signals = {
            "state": SignalState(),
            "application_status": SignalApplicationStatus(),
            "drive": SignalDrive(),
            "config": SignalConfig(),
            "control": SignalControl(),
            "position": SignalPosition(),
            "power": SignalPower(),
        }

        self.client: CommandTelemetryClient | None = None

    def is_connected(self) -> bool:
        """Check if the client is connected.

        Returns
        -------
        `bool`
            True if the client is connected.
        """

        return (self.client is not None) and self.client.connected

    async def connect(self) -> None:
        """Connect to the low-level controller.

        Raises
        ------
        `RuntimeError`
            If the connection times out or is refused.
        """

        await self.disconnect()

        try:
            host = self.connection_information["host"]
            port = self.connection_information["port"]
            self.log.info(f"Connecting to {host}:{port}.")

            self.client = CommandTelemetryClient(
                log=self.log,
                ConfigClass=Config,
                TelemetryClass=Telemetry,
                host=host,
                port=port,
                connect_callback=self.connect_callback,
                config_callback=self.config_callback,
                telemetry_callback=self.telemetry_callback,
            )

            await asyncio.wait_for(
                self.client.start_task,
                timeout=self.connection_information["timeout_connection"],  # type: ignore[arg-type]
            )

        except asyncio.TimeoutError:
            raise RuntimeError("Timed out while connecting to the controller")

        except ConnectionRefusedError:
            raise RuntimeError("Connection refused by the controller.")

        except Exception:
            raise

    async def disconnect(self) -> None:
        """Disconnect from the low-level controller."""

        if self.is_connected():
            try:
                # Workaround the mypy check
                assert self.client is not None

                await self.client.close()

            except Exception:
                self.log.exception("disconnect(): self.client.close() failed")

        self.client = None

    async def connect_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the client socket connects or disconnects.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        if client.should_be_connected and not client.connected:
            self.log.error("Lost connection to the low-level controller")

        if client.connected:
            self.log.info("Connected to the low-level controller")
        else:
            self.log.info("Disconnected from the low-level controller")

    async def config_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the TCP/IP controller outputs configuration.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        self.report_config(client.config)

    async def telemetry_callback(self, client: CommandTelemetryClient) -> None:
        """Called when the TCP/IP controller outputs telemetry.

        Parameters
        ----------
        client : `lsst.ts.hexrotcomm.CommandTelemetryClient`
            TCP/IP client.
        """

        telemetry = client.telemetry
        M_TO_UM = 1e6

        # Report the control data
        timestamp = client.header.tai_sec + client.header.tai_nsec * 1e-9
        self.report_control_data(
            [value * M_TO_UM for value in telemetry.strut_commanded_accel],
            [value * M_TO_UM for value in telemetry.strut_commanded_delta_pos_m],
            timestamp - self._status.timestamp,
        )
        self._status.timestamp = timestamp

        # Report the position
        self.report_position(
            [telemetry.estimated_posfiltvel[idx].pos for idx in range(NUM_STRUT)],
            telemetry.strut_pos_error,
            list(telemetry.measured_xyz) + list(telemetry.measured_uvw),
            self._is_in_motion(telemetry.status_word),
        )

        # Report the power
        self.report_power(telemetry.motor_current, telemetry.bus_voltage)

        # Report the state

        # See ts_hexapod_controller repository for the enum value:
        # AppStatus_CommandByCsc = 0x400
        command_source = (
            CommandSource.CSC
            if (telemetry.application_status & 0x400)
            else CommandSource.GUI
        )
        self.report_state(
            command_source,
            MTHexapod.ControllerState(telemetry.state),
            MTHexapod.EnabledSubstate(telemetry.enabled_substate),
        )

        # Report application status
        self.report_application_status(telemetry.application_status)

        # Report drive status
        self.report_drive_status(
            list(telemetry.status_word),
            list(telemetry.latching_fault_status_register),
            list(telemetry.copley_fault_status_register),
            list(telemetry.input_pin_states),
        )

    def _is_in_motion(self, status_words: list[int]) -> bool:
        """The hexapod is in motion or not.

        Parameters
        ----------
        status_words : `list` [`int`]
            Status words of [strut_0, strut_1, ..., strut_5].

        Returns
        -------
        `bool`
            True if the hexapod is in motion. False otherwise.
        """

        status_total = 0
        for status_word in status_words:
            status_total |= status_word

        # 0x4000 is bit 14 (Amplifier move status)
        return bool(status_total & 0x4000)

    def is_csc_commander(self) -> bool:
        """Commandable SAL component (CSC) is the commander or not.

        Returns
        -------
        `bool`
            True if the CSC is the commander. False otherwise.
        """
        return self._status.command_source == CommandSource.CSC

    async def enable_drives(self, status: bool, time: float = 1.0) -> None:
        """Enable the drives.

        Parameters
        ----------
        status : `bool`
            True if enable the drives. Otherwise, False.
        time : `float`, optional
            Sleep time in second. (the default is 1.0)
        """

        self.assert_is_connected()

        # Workaround the mypy check
        assert self.client is not None

        command = self.make_command(CommandCode.ENABLE_DRIVES, param1=float(status))
        await self.client.run_command(command)

        await asyncio.sleep(time)

    def assert_is_connected(self) -> None:
        """Assert that the client is connected.

        Raises
        ------
        `RuntimeError`
            When the client is not connected.
        """

        if not self.is_connected():
            raise RuntimeError("Not connected to the low-level controller")

    def make_command(
        self,
        code: CommandCode,
        param1: float = 0.0,
        param2: float = 0.0,
        param3: float = 0.0,
        param4: float = 0.0,
        param5: float = 0.0,
        param6: float = 0.0,
    ) -> Command:
        """Make a command from the command identifier and keyword arguments.

        Parameters
        ----------
        code : enum `CommandCode`
            Command to run.
        param1, param2, param3, param4, param5, param6 : `double`, optional
            Command parameters. The meaning of these parameters
            depends on the command code.

        Returns
        -------
        command : `lsst.ts.hexrotcomm.Command`
            The command. Note that the `counter` field is 0;
            it is set by `CommandTelemetryClient.run_command`.
        """

        command = Command()

        # Set the commander to be GUI. See the enum "Commander" in
        # ts_hexrotpxicom.
        command.COMMANDER = 1

        command.code = code.value
        command.param1 = param1
        command.param2 = param2
        command.param3 = param3
        command.param4 = param4
        command.param5 = param5
        command.param6 = param6

        self.log.debug(
            f"New command: {code.name} ({hex(code.value)}): {param1=}, "
            f"{param2=}, {param3=}, {param4=}, {param5=}, {param6=}"
        )

        return command

    def make_command_state(self, trigger_state: TriggerState) -> Command:
        """Make the state command.

        Parameters
        ----------
        trigger_state : enum `TriggerState`
            Trigger state.

        Returns
        -------
        `lsst.ts.hexrotcomm.Command`
            State command.
        """

        if trigger_state == TriggerState.Enable:
            return self.make_command(CommandCode.SET_STATE, param1=2.0)
        elif trigger_state == TriggerState.StandBy:
            return self.make_command(CommandCode.SET_STATE, param1=3.0)
        else:
            # Should be the TriggerState.ClearError
            return self.make_command(CommandCode.SET_STATE, param1=6.0)

    def make_command_enabled_substate(
        self,
        trigger_enabled_substate: TriggerEnabledSubState,
        motion_pattern: MotionPattern,
    ) -> Command:
        """Make the enabled substate command.

        Parameters
        ----------
        trigger_enabled_substate : enum `TriggerEnabledSubState`
            Trigger enabled substate.
        motion_pattern : enum `MotionPattern`
            Motion pattern, synchronous or asynchronous. This is only used
            in the move command.

        Returns
        -------
        `lsst.ts.hexrotcomm.Command`
            Enabled substate command.
        """

        if trigger_enabled_substate == TriggerEnabledSubState.Move:
            return self.make_command(
                CommandCode.SET_ENABLED_SUBSTATE,
                param1=1.0,
                param2=float(motion_pattern.value),
            )
        else:
            # Should be the TriggerEnabledSubState.Stop
            return self.make_command(CommandCode.SET_ENABLED_SUBSTATE, param1=3.0)

    def report_default(self) -> None:
        """Report the default status."""

        signal_state = self.signals["state"]
        signal_state.command_source.emit(  # type: ignore[attr-defined]
            CommandSource.GUI.value
        )
        signal_state.state.emit(  # type: ignore[attr-defined]
            MTHexapod.ControllerState.STANDBY.value
        )
        signal_state.substate_enabled.emit(  # type: ignore[attr-defined]
            MTHexapod.EnabledSubstate.STATIONARY.value
        )

        signal_drive = self.signals["drive"]
        signal_drive.status_word.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.latching_fault.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.copley_status.emit([0] * NUM_STRUT)  # type: ignore[attr-defined]
        signal_drive.input_pin.emit([0x300C0] * NUM_DRIVE)  # type: ignore[attr-defined]

        signal_application_status = self.signals["application_status"]
        signal_application_status.status.emit(0)  # type: ignore[attr-defined]

        self.report_config(Config())
        self.report_control_data([0.0] * NUM_STRUT, [0.0] * NUM_STRUT, 0.0)
        self.report_position(
            [0.0] * NUM_STRUT, [0.0] * NUM_STRUT, [0.0] * NUM_DEGREE_OF_FREEDOM, False
        )
        self.report_power([0.0] * NUM_STRUT, [0.0] * NUM_DRIVE)

    def report_config(self, config: Config) -> None:
        """Report the configuration.

        Parameters
        ----------
        config : `Config`
            Configuration details.
        """

        self.signals["config"].config.emit(config)  # type: ignore[attr-defined]

    def report_control_data(
        self,
        command_acceleration: list[float],
        command_position: list[float],
        time_difference: float,
    ) -> None:
        """Report the control data.

        Parameters
        ----------
        command_acceleration : `list` [`float`]
            Commanded accelerations of [strut_0, strut_1, ..., strut_5] in
            um/sec^2.
        command_position : `list` [`float`]
            Commanded positions of [strut_0, strut_1, ..., strut_5] in um.
        time_difference : `float`
            Time frame difference in seconds.
        """

        signal = self.signals["control"]
        signal.command_acceleration.emit(command_acceleration)  # type: ignore[attr-defined]
        signal.command_position.emit(command_position)  # type: ignore[attr-defined]
        signal.time_difference.emit(time_difference)  # type: ignore[attr-defined]

    def report_position(
        self,
        strut_position: list[float],
        strut_position_error: list[float],
        hexapod_position: list[float],
        in_motion: bool,
    ) -> None:
        """Report the position.

        Parameters
        ----------
        strut_position : `list` [`float`]
            Strut positions of [strut_0, strut_1, ..., strut_5] in micron.
        strut_position_error : list` [`float`]
            Strut position errors of [strut_0, strut_1, ..., strut_5] in
            micron.
        hexapod_position : list` [`float`]
            Hexapod positions of [x, y, z, rx, ry, rz] in micron and degree.
        in_motion : `bool`
            Hexapod is in motion or not.
        """

        signal = self.signals["position"]
        signal.strut_position.emit(strut_position)  # type: ignore[attr-defined]
        signal.strut_position_error.emit(strut_position_error)  # type: ignore[attr-defined]
        signal.hexapod_position.emit(hexapod_position)  # type: ignore[attr-defined]
        signal.in_motion.emit(in_motion)  # type: ignore[attr-defined]

    def report_power(self, current: list[float], voltage: list[float]) -> None:
        """Report the power.

        Parameters
        ----------
        current : `list` [`float`]
            Currents of [strut_0, strut_1, ..., strut_5] in ampere.
        voltage : `list` [`float`]
            Bus voltages of [drive_0, drive_1, drive_2] in volts.
        """

        signal = self.signals["power"]
        signal.current.emit(current)  # type: ignore[attr-defined]
        signal.voltage.emit(voltage)  # type: ignore[attr-defined]

    def report_state(
        self,
        command_source: CommandSource,
        state: MTHexapod.ControllerState,
        substate_enabled: MTHexapod.EnabledSubstate,
    ) -> None:
        """Report the controller's state.

        Parameters
        ----------
        command_source : enum `CommandSource`
            Command source.
        state : enum `MTHexapod.ControllerState`
            State.
        substate_enabled : enum `MTHexapod.EnabledSubstate`
            Enabled substate.
        """

        signal = self.signals["state"]

        self._compare_status_and_report(
            "command_source",
            command_source.value,
            signal.command_source,  # type: ignore[attr-defined]
        )
        self._compare_status_and_report("state", state.value, signal.state)  # type: ignore[attr-defined]
        self._compare_status_and_report(
            "substate_enabled", substate_enabled.value, signal.substate_enabled  # type: ignore[attr-defined]
        )

    def _compare_status_and_report(
        self, field: str, value: typing.Any, signal: Signal
    ) -> None:
        """Compare the value with current status and report it if different.

        Parameters
        ----------
        field : `str`
            Field of the status.
        value : `typing.Any`
            Value.
        signal : `PySide6.QtCore.Signal`
            Signal.

        Raises
        ------
        `TypeError`
            When the type of value does not match with the type of status's
            value.
        """

        status_value = getattr(self._status, field)
        if type(value) is not type(status_value):
            raise TypeError(
                f"Type of value ({type(value)}) does not match with type of "
                f"status's value ({type(status_value)})."
            )

        if value != status_value:
            signal.emit(value)
            setattr(self._status, field, value)

            self.log.info(f"Update system status: {field} = {value}")

    def report_application_status(self, status: int) -> None:
        """Report the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        signal = self.signals["application_status"]

        self._compare_status_and_report(
            "application_status", status, signal.status  # type: ignore[attr-defined]
        )

    def report_drive_status(
        self,
        status_word: list[int],
        latching_fault: list[int],
        copley_status: list[int],
        input_pin: list[int],
    ) -> None:
        """Report the drive status.

        Parameters
        ----------
        status_word : `list` [`int`]
            Status word of [strut_0, strut_1, ..., strut_5].
        latching_fault : `list` [`int`]
            Latching fault status of [strut_0, strut_1, ..., strut_5].
        copley_status : `list` [`int`]
            Copley drive status of [strut_0, strut_1, ..., strut_5].
        input_pin : `list` [`int`]
            Input pin status of [drive_0, drive_1, drive_2].
        """

        signal = self.signals["drive"]

        self._compare_status_and_report(
            "status_word", status_word, signal.status_word  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "latching_fault", latching_fault, signal.latching_fault  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "copley_status", copley_status, signal.copley_status  # type: ignore[attr-defined]
        )
        self._compare_status_and_report(
            "input_pin", input_pin, signal.input_pin  # type: ignore[attr-defined]
        )
