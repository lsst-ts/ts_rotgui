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

__all__ = ["TabTelemetry"]

from lsst.ts.guitool import (
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
    update_boolean_indicator_status,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..model import Model
from ..signals import (
    SignalApplicationStatus,
    SignalControl,
    SignalPositionVelocity,
    SignalPower,
)


class TabTelemetry(TabTemplate):
    """Table of the telemetry.

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

        self._telemetry = {
            "position_command": create_label(),
            "position_current": create_label(),
            "rate_command_a": create_label(),
            "rate_feedback_a": create_label(),
            "motor_torque_a": create_label(),
            "rate_command_b": create_label(),
            "rate_feedback_b": create_label(),
            "motor_torque_b": create_label(),
            "application_status_word": create_label(),
            "time_frame_difference": create_label(),
            "current_a": create_label(),
            "current_b": create_label(),
        }

        self._indicators = {
            "application_status": create_radio_indicators(16),
            "simulink_flag": create_radio_indicators(11),
        }

        self.set_widget_and_layout()

        self._set_signal_application_status(
            self.model.signals["application_status"]  # type: ignore[arg-type]
        )
        self._set_signal_control(
            self.model.signals["control"]  # type: ignore[arg-type]
        )
        self._set_signal_position_velocity(
            self.model.signals["position_velocity"]  # type: ignore[arg-type]
        )
        self._set_signal_power(self.model.signals["power"])  # type: ignore[arg-type]

    def create_layout(self) -> QVBoxLayout:
        layout_telemetry = QVBoxLayout()
        layout_telemetry.addWidget(self._create_group_position())
        layout_telemetry.addWidget(self._create_group_control_data())
        layout_telemetry.addWidget(self._create_group_power())

        layout_simulink_flag = QVBoxLayout()
        layout_simulink_flag.addWidget(self._create_group_time())
        layout_simulink_flag.addWidget(self._create_group_simulink_flag())

        layout_application_status = QVBoxLayout()
        layout_application_status.addWidget(self._create_group_application_status())

        layout = QHBoxLayout()
        layout.addLayout(layout_telemetry)
        layout.addLayout(layout_simulink_flag)
        layout.addLayout(layout_application_status)

        return layout

    def _create_group_position(self) -> QGroupBox:
        """Create the group of position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Rotator command:", self._telemetry["position_command"])
        layout.addRow("Rotator position:", self._telemetry["position_current"])

        return create_group_box("Position", layout)

    def _create_group_control_data(self) -> QGroupBox:
        """Create the group of control data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Rate command A:", self._telemetry["rate_command_a"])
        layout.addRow("Rate command B:", self._telemetry["rate_command_b"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Rate feedback A:", self._telemetry["rate_feedback_a"])
        layout.addRow("Rate feedback B:", self._telemetry["rate_feedback_b"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Motor torque A:", self._telemetry["motor_torque_a"])
        layout.addRow("Motor torque B:", self._telemetry["motor_torque_b"])

        return create_group_box("Control Data", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def _create_group_power(self) -> QGroupBox:
        """Create the group of power data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Current A:", self._telemetry["current_a"])
        layout.addRow("Current B:", self._telemetry["current_b"])

        return create_group_box("Power", layout)

    def _create_group_time(self) -> QGroupBox:
        """Create the group of time data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Time frame difference:", self._telemetry["time_frame_difference"])

        return create_group_box("Time Data", layout)

    def _create_group_application_status(self) -> QGroupBox:
        """Create the group of application status.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Status word:", self._telemetry["application_status_word"])
        self.add_empty_row_to_form_layout(layout)

        names = [
            "Following error",
            "Move complete",
            "GUI connected",
            "Relative move commanded",
            "Synchronous move",
            "Invalid command or value",
            "Safety interlock fault",
            "Extend limit switch",
            "Retract limit switch",
            "EtherCAT not ready",
            "Command source = CSC",
            "Motion timeout",
            "CSC connected",
            "Drive fault",
            "Simulink fault declared",
            "Linear encoder fault",
        ]
        for name, indicator in zip(names, self._indicators["application_status"]):
            layout.addRow(f"{name}:", indicator)

        # Disable some unused indicators at the moment
        for idx in (0, 1, 3, 4, 11):
            item = layout.itemAt(2 * (idx + 1) + 1).widget()
            item.setEnabled(False)

        return create_group_box("Application Status", layout)

    def _create_group_simulink_flag(self) -> QGroupBox:
        """Create the group of Simulink flag.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        names = [
            "Initialization complete",
            "Slew complete",
            "Point-to-Point move complete",
            "New point-to-point command",
            "Stop complete",
            "Following error",
            "Move success",
            "Tracking success",
            "Position feedback fault",
            "Tracking lost",
            "No new track command error",
        ]
        for name, indicator in zip(names, self._indicators["simulink_flag"]):
            layout.addRow(f"{name}:", indicator)

        return create_group_box("Simulink Flag", layout)

    def _set_signal_application_status(self, signal: SignalApplicationStatus) -> None:
        """Set the application status signal.

        Parameters
        ----------
        signal : `SignalApplicationStatus`
            Signal.
        """

        signal.status.connect(self._callback_application_status)
        signal.simulink_flag.connect(self._callback_simulink_flag)

    @asyncSlot()
    async def _callback_application_status(self, status: int) -> None:
        """Callback of the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        self._update_application_status(status)

    def _update_application_status(self, status: int) -> None:
        """Update the application status.

        Parameters
        ----------
        status : `int`
            Application status.
        """

        self._telemetry["application_status_word"].setText(hex(status))

        faults = [0, 5, 6, 7, 8, 9, 11, 13, 14, 15]
        self._update_boolean_indicators(status, self._indicators["application_status"], faults)

    def _update_boolean_indicators(
        self, status: int, indicators: list[QRadioButton], faults: list[int]
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
        """

        for idx, indicator in enumerate(indicators):
            update_boolean_indicator_status(
                indicator,
                status & (1 << idx),
                is_fault=(idx in faults),
            )

    @asyncSlot()
    async def _callback_simulink_flag(self, status: int) -> None:
        """Callback of the Simulink flag.

        Parameters
        ----------
        status : `int`
            Simulink flag.
        """

        self._update_simulink_flag(status)

    def _update_simulink_flag(self, status: int) -> None:
        """Update the Simulink flag.

        Parameters
        ----------
        status : `int`
            Simulink flag.
        """

        faults = [5, 8, 9, 10]
        self._update_boolean_indicators(status, self._indicators["simulink_flag"], faults)

    def _set_signal_control(self, signal: SignalControl) -> None:
        """Set the control signal.

        Parameters
        ----------
        signal : `SignalControl`
            Signal.
        """

        signal.rate_command.connect(self._callback_rate_command)
        signal.rate_feedback.connect(self._callback_rate_feedback)
        signal.torque.connect(self._callback_torque)
        signal.time_difference.connect(self._callback_time_difference)

    @asyncSlot()
    async def _callback_rate_command(self, rates: list[float]) -> None:
        """Callback of the commanded rates.

        Parameters
        ----------
        rates : `list` [`float`]
            Rates in deg/sec.
        """

        self._telemetry["rate_command_a"].setText(f"{rates[0]:.7f} deg/sec")
        self._telemetry["rate_command_b"].setText(f"{rates[1]:.7f} deg/sec")

    @asyncSlot()
    async def _callback_rate_feedback(self, rates: list[float]) -> None:
        """Callback of the feedback rates.

        Parameters
        ----------
        rates : `list` [`float`]
            Rates in deg/sec.
        """

        self._telemetry["rate_feedback_a"].setText(f"{rates[0]:.7f} deg/sec")
        self._telemetry["rate_feedback_b"].setText(f"{rates[1]:.7f} deg/sec")

    @asyncSlot()
    async def _callback_torque(self, torques: list[float]) -> None:
        """Callback of the motor torques.

        Parameters
        ----------
        torques : `list` [`float`]
            Torques in N*m.
        """

        self._telemetry["motor_torque_a"].setText(f"{torques[0]:.7f} N*m")
        self._telemetry["motor_torque_b"].setText(f"{torques[1]:.7f} N*m")

    @asyncSlot()
    async def _callback_time_difference(self, time_difference: float) -> None:
        """Callback of the time frame difference.

        Parameters
        ----------
        time_difference : `float`
            Time difference in seconds.
        """

        self._telemetry["time_frame_difference"].setText(f"{time_difference:.7f} sec")

    def _set_signal_position_velocity(self, signal: SignalPositionVelocity) -> None:
        """Set the position-velocity signal.

        Parameters
        ----------
        signal : `SignalPositionVelocity`
            Signal.
        """

        signal.position_current.connect(self._callback_position_current)
        signal.position_command.connect(self._callback_position_command)

    @asyncSlot()
    async def _callback_position_current(self, position: float) -> None:
        """Callback of the current position.

        Parameters
        ----------
        position : `float`
            Position in deg.
        """

        self._telemetry["position_current"].setText(f"{position:.7f} deg")

    @asyncSlot()
    async def _callback_position_command(self, position: float) -> None:
        """Callback of the commanded position.

        Parameters
        ----------
        position : `float`
            Position in deg.
        """

        self._telemetry["position_command"].setText(f"{position:.7f} deg")

    def _set_signal_power(self, signal: SignalPower) -> None:
        """Set the power signal.

        Parameters
        ----------
        signal : `SignalPower`
            Signal.
        """

        signal.current.connect(self._callback_current)

    @asyncSlot()
    async def _callback_current(self, currents: list[float]) -> None:
        """Callback of the current.

        Parameters
        ----------
        currents : `list` [`float`]
            Currents of [axis_a, axis_b] in ampere.
        """

        self._telemetry["current_a"].setText(f"{currents[0]:.6f} A")
        self._telemetry["current_b"].setText(f"{currents[1]:.6f} A")
