# This file is part of ts_rotgui.
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

__all__ = ["TabDriveStatus"]

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_radio_indicators,
    update_boolean_indicator_status,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalDrive


class TabDriveStatus(TabTemplate):
    """Table of the drive status.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        self.model = model

        # 16 bits
        self._list_status_word = {
            "axis_a": create_radio_indicators(16),
            "axis_b": create_radio_indicators(16),
        }

        # 16 bits
        self._list_latching_fault_status = {
            "axis_a": create_radio_indicators(16),
            "axis_b": create_radio_indicators(16),
        }

        # 32 bits
        self._list_copley_status = {
            "axis_a": create_radio_indicators(32),
            "axis_b": create_radio_indicators(32),
        }

        # Only 3 bits are used
        self._list_input_pin_state = {
            "axis_a": create_radio_indicators(3),
            "axis_b": create_radio_indicators(3),
        }

        self.set_widget_and_layout(is_scrollable=True)

        self._set_signal_drive(self.model.signals["drive"])  # type: ignore[arg-type]

    def create_layout(self) -> QVBoxLayout:

        # First column
        layout_drive = QVBoxLayout()
        layout_drive.addWidget(self._create_group_status_word())
        layout_drive.addWidget(self._create_group_latching_fault_status())

        # Second column
        layout_copley = QVBoxLayout()
        layout_copley.addWidget(self._create_group_copley_status())
        layout_copley.addWidget(self._create_group_input_pin_state())

        layout = QHBoxLayout()
        layout.addLayout(layout_drive)
        layout.addLayout(layout_copley)

        return layout

    def _create_group_status_word(self) -> QGroupBox:
        """Create the group box for the status word (0x6041).

        Returns
        -------
        `QGroupBox`
            Group box for the status word (0x6041).
        """

        names = [
            "Bit 0 - Ready to switch on:",
            "Bit 1 - Switched on:",
            "Bit 2 - Operation enabled:",
            "Bit 3 - Fault latched:",
            "Bit 4 - Voltage enabled:",
            "Bit 5 - Reserved:",
            "Bit 6 - Switch on disabled:",
            "Bit 7 - Warning:",
            "Bit 8 - Last trajectory aborted:",
            "Bit 9 - Remote:",
            "Bit 10 - Reserved:",
            "Bit 11 - Internal limit active:",
            "Bit 12 - Reserved:",
            "Bit 13 - Reserved:",
            "Bit 14 - Reserved:",
            "Bit 15 - Reserved:",
        ]
        return create_group_box(
            "Status Word (0x6041)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [self._list_status_word["axis_a"], self._list_status_word["axis_b"]]
                ),
            ),
        )

    def _combine_indicators(
        self, list_indicators: list[list[QRadioButton]]
    ) -> list[QHBoxLayout]:
        """Combine the indicators.

        Parameters
        ----------
        list_indicators : `list` [ `list` [`QRadioButton`] ]
            List of indicators.

        Returns
        -------
        combined_indicators : `list` [`QHBoxLayout`]
            Combined indicators.
        """

        combined_indicators = list()

        num_list = len(list_indicators)
        num_indicator_per_list = len(list_indicators[0])

        for idx_indicator in range(num_indicator_per_list):
            combined_indicator = QHBoxLayout()

            for idx_list in range(num_list):
                combined_indicator.addWidget(list_indicators[idx_list][idx_indicator])

            combined_indicators.append(combined_indicator)

        return combined_indicators

    def _create_form_layout(
        self, names: list[str], items: list[QWidget | QLayout]
    ) -> QFormLayout:
        """Create a form layout.

        Parameters
        ----------
        names : `list` [`str`]
            Names.
        items : `list` [`QWidget` or `QLayout`]
            Items.

        Returns
        -------
        layout : `QFormLayout`
            Form layout.
        """

        layout = QFormLayout()
        for name, item in zip(names, items):
            layout.addRow(name, item)

        return layout

    def _create_group_latching_fault_status(self) -> QGroupBox:
        """Create the group box for the latching fault status (0x2183).

        Returns
        -------
        `QGroupBox`
            Group box for the latching fault status (0x2183).
        """

        names = [
            "Bit 0 - Data flash CRC failure:",
            "Bit 1 - Amplifier internal error:",
            "Bit 2 - Short circuit:",
            "Bit 3 - Amplifier over temperature:",
            "Bit 4 - Motor over temperature:",
            "Bit 5 - Over voltage:",
            "Bit 6 - Under voltage:",
            "Bit 7 - Feedback fault:",
            "Bit 8 - Phasing error:",
            "Bit 9 - Tracking error:",
            "Bit 10 - Over current:",
            "Bit 11 - FPGA failure 1:",
            "Bit 12 - Command input lost:",
            "Bit 13 - FPGA failure 2:",
            "Bit 14 - Safety circuit fault:",
            "Bit 15 - Unable to control current:",
        ]
        return create_group_box(
            "Latching Fault Status (0x2183)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_latching_fault_status["axis_a"],
                        self._list_latching_fault_status["axis_b"],
                    ]
                ),
            ),
        )

    def _create_group_copley_status(self) -> QGroupBox:
        """Create the group box for the Copley status (0x2180).

        Returns
        -------
        `QGroupBox`
            Group box for the Copley status (0x2180).
        """

        names = [
            "Bit 0 - Short circuit detected:",
            "Bit 1 - Amplifier over temperature:",
            "Bit 2 - Over voltage:",
            "Bit 3 - Under voltage:",
            "Bit 4 - Motor over temperature:",
            "Bit 5 - Feedback error:",
            "Bit 6 - Motor phasing error:",
            "Bit 7 - Current output limited:",
            "Bit 8 - Voltage output limited:",
            "Bit 9 - Negative limit switch active:",
            "Bit 10 - Positive limit switch active:",
            "Bit 11 - Enable input not active:",
            "Bit 12 - Amp is disabled by software:",
            "Bit 13 - Trying to stop motor:",
            "Bit 14 - Motor brake activated:",
            "Bit 15 - PWM outputs disabled:",
            "Bit 16 - Positive software limit condition:",
            "Bit 17 - Negative software limit condition:",
            "Bit 18 - Tracking error:",
            "Bit 19 - Tracking warning:",
            "Bit 20 - Amplifier in reset state:",
            "Bit 21 - Position counts wrapped:",
            "Bit 22 - Amplifier fault:",
            "Bit 23 - At velocity limit:",
            "Bit 24 - At acceleration limit:",
            "Bit 25 - Position error > tracking window:",
            "Bit 26 - Home switch is active:",
            "Bit 27 - In motion:",
            "Bit 28 - Velocity error > tracking window:",
            "Bit 29 - Phasing not set:",
            "Bit 30 - Command fault:",
            "Bit 31 - Not used:",
        ]
        return create_group_box(
            "Copley Status (0x2180)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_copley_status["axis_a"],
                        self._list_copley_status["axis_b"],
                    ]
                ),
            ),
        )

    def _create_group_input_pin_state(self) -> QGroupBox:
        """Create the group box for the input pin state (0x219A).

        Returns
        -------
        `QGroupBox`
            Group box for the input pin state (0x219A).
        """

        names = [
            "Bit 6 - Safety interlock OK:",
            "Bit 7 - Extend limit switch hit:",
            "Bit 8 - Retract limit switch hit:",
        ]
        return create_group_box(
            "Input Pin State (0x219A)",
            self._create_form_layout(
                names,
                self._combine_indicators(
                    [
                        self._list_input_pin_state["axis_a"],
                        self._list_input_pin_state["axis_b"],
                    ]
                ),
            ),
        )

    def _set_signal_drive(self, signal: SignalDrive) -> None:
        """Set the drive signal.

        Parameters
        ----------
        signal : `SignalDrive`
            Signal.
        """

        signal.status_word.connect(self._callback_status_word)
        signal.latching_fault.connect(self._callback_latching_fault)
        signal.copley_status.connect(self._callback_copley_status)
        signal.input_pin.connect(self._callback_input_pin)

    @asyncSlot()
    async def _callback_status_word(self, status_word: list[int]) -> None:
        """Callback of the status word.

        Parameters
        ----------
        status_word : `list` [`int`]
            Status word of [axia_a, axis_b].
        """

        self._update_status_word(status_word[0], "axis_a")
        self._update_status_word(status_word[1], "axis_b")

    def _update_status_word(self, status: int, actuator: str) -> None:
        """Update the status word.

        Parameters
        ----------
        status : `int`
            Status word.
        actuator : `str`
            Actuator ("axis_a" or "axis_b").
        """

        faults = [3]
        warnings = [6, 7, 8, 11]
        self._update_boolean_indicators(
            status,
            self._list_status_word[actuator],
            faults,
            warnings,
            [],
        )

    def _update_boolean_indicators(
        self,
        status: int,
        indicators: list[QRadioButton],
        faults: list[int],
        warnings: list[int],
        default_errors: list[int],
    ) -> None:
        """Update the boolean indicators.

        Parameters
        ----------
        status : `int`
            Status.
        indicators : `list` [`QRadioButton`]
            Indicators.
        faults : `list` [`int`]
            Indexes of the faults.
        warnings : `list` [`int`]
            Indexes of the warnings.
        default_errors : `list` [`int`]
            Default errors.
        """

        for idx, indicator in enumerate(indicators):
            update_boolean_indicator_status(
                indicator,
                status & (1 << idx),
                is_fault=(idx in faults),
                is_warning=(idx in warnings),
                is_default_error=(idx in default_errors),
            )

    @asyncSlot()
    async def _callback_latching_fault(self, latching_fault: list[int]) -> None:
        """Callback of the latching fault.

        Parameters
        ----------
        latching_fault : `list` [`int`]
            Latching fault status of [axia_a, axis_b].
        """

        self._update_latching_fault_status(latching_fault[0], "axis_a")
        self._update_latching_fault_status(latching_fault[1], "axis_b")

    def _update_latching_fault_status(self, status: int, actuator: str) -> None:
        """Update the latching fault status.

        Parameters
        ----------
        status : `int`
            Status word.
        actuator : `str`
            Actuator ("axis_a" or "axis_b").
        """

        faults = list(range(16))
        self._update_boolean_indicators(
            status,
            self._list_latching_fault_status[actuator],
            faults,
            [],
            [],
        )

    @asyncSlot()
    async def _callback_copley_status(self, copley_status: list[int]) -> None:
        """Callback of the Copley drive status.

        Parameters
        ----------
        copley_status : `list` [`int`]
            Copley drive status of [axia_a, axis_b].
        """

        self._update_copley_status(copley_status[0], "axis_a")
        self._update_copley_status(copley_status[1], "axis_b")

    def _update_copley_status(self, status: int, actuator: str) -> None:
        """Update the Copley drive status.

        Parameters
        ----------
        status : `int`
            Status word.
        actuator : `str`
            Actuator ("axis_a" or "axis_b").
        """

        faults = [0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 18, 22, 28, 29, 30]
        warnings = [7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25]
        self._update_boolean_indicators(
            status,
            self._list_copley_status[actuator],
            faults,
            warnings,
            [],
        )

    @asyncSlot()
    async def _callback_input_pin(self, input_pin: list[int]) -> None:
        """Callback of the input pin status.

        Parameters
        ----------
        input_pin : `list` [`int`]
            Input pin status of [axia_a, axis_b].
        """

        self._update_input_pin_status(input_pin[0], "axis_a")
        self._update_input_pin_status(input_pin[1], "axis_b")

    def _update_input_pin_status(self, status: int, actuator: str) -> None:
        """Update the input pin status.

        Parameters
        ----------
        status : `int`
            Status word.
        actuator : `str`
            Actuator ("axis_a" or "axis_b").
        """

        bit_offset = 5

        faults = [1, 2]
        default_errors = [0]
        self._update_boolean_indicators(
            status >> bit_offset,
            self._list_input_pin_state[actuator],
            faults,
            [],
            default_errors,
        )
