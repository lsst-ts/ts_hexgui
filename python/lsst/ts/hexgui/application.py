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

__all__ = ["run_hexgui", "check_arguments"]

import asyncio
import functools

import qasync
from lsst.ts.guitool import base_frame_run_application
from lsst.ts.xml.enums import MTHexapod
from PySide6.QtCore import QCommandLineOption, QCommandLineParser

from .main_window import MainWindow


def run_hexgui() -> None:
    """Run the hexapod GUI."""
    base_frame_run_application(main)


async def main(argv: list) -> bool:
    """Main application.

    Parameters
    ----------
    argv : `list`
        Arguments from the command line.
    """

    # The set of "aboutToQuit" comes from "qasync/examples/aiohttp_fetch.py"
    loop = asyncio.get_event_loop()
    future: asyncio.Future = asyncio.Future()

    # You need one (and only one) QApplication instance per application.
    # There is one QApplication instance in "qasync" already.
    app = qasync.QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(cancel_future, future, loop)
        )

    app.setApplicationName("Hexapod EUI")

    # Set the parser
    parser = QCommandLineParser()
    parser.setApplicationDescription("Run the hexapod graphical user interface (GUI).")
    parser.addHelpOption()

    parser.addPositionalArgument("hexapod", "1: camera hexapod, 2: M2 hexapod.")

    option_verbose = QCommandLineOption(
        ["v", "verbose"], "Print log messages to terminal."
    )
    parser.addOption(option_verbose)

    option_simulation = QCommandLineOption(
        ["s", "simulation"], "Run the simulation mode."
    )
    parser.addOption(option_simulation)

    option_log_level = QCommandLineOption(
        ["d", "debuglevel"],
        (
            "Debug logging level: CRITICAL (50), ERROR (40), WARNING (30), "
            "INFO (20), DEBUG (10), NOTSET (0). The default is 20."
        ),
        "level",
        "20",
    )
    parser.addOption(option_log_level)

    option_no_log_file = QCommandLineOption(
        ["no-logfile"], "Do not write log messages to file."
    )
    parser.addOption(option_no_log_file)

    parser.process(app)

    # Get the argument and check the values
    args = parser.positionalArguments()
    check_arguments(args)

    is_output_log_to_file = not parser.isSet(option_no_log_file)
    is_verbose = parser.isSet(option_verbose)
    is_simulation_mode = parser.isSet(option_simulation)
    log_level = int(parser.value(option_log_level))

    # Create a Qt main window, which will be our window.
    window_main = MainWindow(
        is_output_log_to_file,
        is_verbose,
        MTHexapod.SalIndex(int(args[0])),
        is_simulation_mode,
        log_level=log_level,
    )
    window_main.show()

    await future

    # Your application won't reach here until you exit and the event
    # loop has stopped.
    return True


def check_arguments(args: list) -> None:
    """Check the arguments.

    Parameters
    ----------
    args : `list`
        Arguments from the command line.

    Raises
    ------
    `ValueError`
        If the number of arguments is not 1.
    `ValueError`
        If the argument is not 1 or 2.
    """

    if len(args) != 1:
        raise ValueError("The number of arguments must be 1.")

    if args[0] not in ["1", "2"]:
        raise ValueError("The argument must be 1 or 2.")


def cancel_future(future: asyncio.Future, loop: asyncio.AbstractEventLoop) -> None:
    """Cancel the future.

    This is needed to ensure that all pre- and post-processing for the event
    loop is done. See the source code in qasync library for the details.

    Parameters
    ----------
    future : `asyncio.Future`
        Future.
    loop : `asyncio.unix_events._UnixSelectorEventLoop`
        Event loop.
    """

    loop.call_later(10, future.cancel)
    if not future.cancelled():
        future.cancel()
