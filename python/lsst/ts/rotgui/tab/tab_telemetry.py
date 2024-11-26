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
    ButtonStatus,
    TabTemplate,
    create_group_box,
    create_label,
    create_radio_indicators,
    update_button_color,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QVBoxLayout

from ..model import Model


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
            "position_actual": create_label(),
            "rate_command_a": create_label(),
            "rate_feedback_a": create_label(),
            "motor_torque_a": create_label(),
            "rate_command_b": create_label(),
            "rate_feedback_b": create_label(),
            "motor_torque_b": create_label(),
            "application_status_word": create_label(),
            "time_frame_difference": create_label(),
        }

        self._configuration = {
            "velocity_limit": create_label(),
            "acceleration_limit": create_label(),
            "position_error_threshold": create_label(),
            "upper_position_limit": create_label(),
            "lower_position_limit": create_label(),
            "following_error_threshold": create_label(),
            "tracking_lost_timeout": create_label(),
            "tracking_success_threshold": create_label(),
            "drives_enabled": create_label(),
        }

        self._indicators = {
            "application_status": create_radio_indicators(16),
            "simulink_flag": create_radio_indicators(11),
        }

        self._set_default()

        self.set_widget_and_layout(is_scrollable=True)

    def create_layout(self) -> QVBoxLayout:

        layout_telemetry = QVBoxLayout()
        layout_telemetry.addWidget(self._create_group_position())
        layout_telemetry.addWidget(self._create_group_control_data())
        layout_telemetry.addWidget(self._create_group_configuration())
        layout_telemetry.addWidget(self._create_group_time())

        layout_application_status = QVBoxLayout()
        layout_application_status.addWidget(self._create_group_application_status())
        layout_application_status.addWidget(self._create_group_simulink_flag())

        layout = QHBoxLayout()
        layout.addLayout(layout_telemetry)
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
        layout.addRow("Rotator position:", self._telemetry["position_actual"])

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

    def _create_group_configuration(self) -> QGroupBox:
        """Create the group of configuration.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Velocity limit:", self._configuration["velocity_limit"])
        layout.addRow("Acceleration limit:", self._configuration["acceleration_limit"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow(
            "Upper position limit:", self._configuration["upper_position_limit"]
        )
        layout.addRow(
            "Lower position limit:", self._configuration["lower_position_limit"]
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow(
            "Position error threshold:", self._configuration["position_error_threshold"]
        )
        layout.addRow(
            "Following error threshold:",
            self._configuration["following_error_threshold"],
        )
        layout.addRow(
            "Tracking success threshold:",
            self._configuration["tracking_success_threshold"],
        )
        layout.addRow(
            "Tracking lost timeout:", self._configuration["tracking_lost_timeout"]
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Drives enabled:", self._configuration["drives_enabled"])

        return create_group_box("Configuration Settings", layout)

    def _create_group_time(self) -> QGroupBox:
        """Create the group of time data.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Time frame difference:", self._telemetry["time_frame_difference"]
        )

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
            "No new track command error:",
        ]
        for name, indicator in zip(names, self._indicators["simulink_flag"]):
            layout.addRow(f"{name}:", indicator)

        return create_group_box("Simulink Flag", layout)

    def _set_default(self) -> None:
        """Set the default values."""

        # Telemetry
        self._telemetry["position_command"].setText("0 deg")
        self._telemetry["position_actual"].setText("0 deg")

        self._telemetry["rate_command_a"].setText("0 deg/sec")
        self._telemetry["rate_feedback_a"].setText("0 deg/sec")
        self._telemetry["motor_torque_a"].setText("0 N*m")

        self._telemetry["rate_command_b"].setText("0 deg/sec")
        self._telemetry["rate_feedback_b"].setText("0 deg/sec")
        self._telemetry["motor_torque_b"].setText("0 N*m")

        self._telemetry["application_status_word"].setText("0x0")

        self._telemetry["time_frame_difference"].setText("0 sec")

        # Configuration
        self._configuration["velocity_limit"].setText("0 deg/sec")
        self._configuration["acceleration_limit"].setText("0 deg/sec^2")

        self._configuration["position_error_threshold"].setText("0 deg")
        self._configuration["upper_position_limit"].setText("0 deg")
        self._configuration["lower_position_limit"].setText("0 deg")

        self._configuration["following_error_threshold"].setText("0 deg")

        self._configuration["tracking_lost_timeout"].setText("0 sec")
        self._configuration["tracking_success_threshold"].setText("0 deg")

        self._configuration["drives_enabled"].setText("False")

        # Set the default indicators
        for indicators in self._indicators.values():
            for indicator in indicators:
                update_button_color(indicator, QPalette.Base, ButtonStatus.Default)
