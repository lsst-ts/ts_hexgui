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

import asyncio
import shutil

import pytest

from lsst.ts.hexgui.application import check_arguments


@pytest.mark.asyncio
async def test_run_hexgui() -> None:
    # Make sure this application exists
    application_name = "run_hexgui"
    exe_path = shutil.which(application_name)

    assert exe_path is not None

    # Run the process and get the standard output
    process = await asyncio.create_subprocess_exec(
        application_name,
        "-h",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _ = await process.communicate()

    # If there is the error, the result will be empty
    assert stdout.decode() != ""


def test_check_arguments() -> None:
    # Test the case with no arguments
    with pytest.raises(ValueError):
        check_arguments([])

    # Test the case with wrong argument
    with pytest.raises(ValueError):
        check_arguments(["wrong_argument"])

    # Test the case with two arguments
    with pytest.raises(ValueError):
        check_arguments(["1", "2"])

    # Test the case with the correct arguments
    check_arguments(["1"])
