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

__all__ = ["TabConfig"]

from lsst.ts.guitool import TabTemplate, create_group_box, create_label
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QGroupBox, QVBoxLayout
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalConfig
from ..structs import Config


class TabConfig(TabTemplate):
    """Table of the configuration.

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

        self._configuration = {
            "max_velocity_limit": create_label(),
            "velocity_limit": create_label(),
            "acceleration_limit": create_label(),
            "position_error_threshold": create_label(),
            "upper_position_limit": create_label(),
            "lower_position_limit": create_label(),
            "disable_limit_max_time": create_label(),
            "following_error_threshold": create_label(),
            "tracking_lost_timeout": create_label(),
            "tracking_success_threshold": create_label(),
            "emergency_jerk_limit": create_label(),
            "emergency_acceleration_limit": create_label(),
            "drives_enabled": create_label(),
        }

        self.set_widget_and_layout()

        self._set_signal_config(self.model.signals["config"])  # type: ignore[arg-type]

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_configuration())

        return layout

    def _create_group_configuration(self) -> QGroupBox:
        """Create the group of configuration.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Maximum velocity limit:", self._configuration["max_velocity_limit"]
        )
        layout.addRow("Velocity limit:", self._configuration["velocity_limit"])
        layout.addRow("Acceleration limit:", self._configuration["acceleration_limit"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow(
            "Upper position limit:", self._configuration["upper_position_limit"]
        )
        layout.addRow(
            "Lower position limit:", self._configuration["lower_position_limit"]
        )
        layout.addRow(
            "Disable limit maximum time:", self._configuration["disable_limit_max_time"]
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

        layout.addRow(
            "Emergency acceleration limit:",
            self._configuration["emergency_acceleration_limit"],
        )
        layout.addRow(
            "Emergency jerk limit:", self._configuration["emergency_jerk_limit"]
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Drives enabled:", self._configuration["drives_enabled"])

        return create_group_box("Configuration Settings", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def _set_signal_config(self, signal: SignalConfig) -> None:
        """Set the config signal.

        Parameters
        ----------
        signal : `SignalConfig`
            Signal.
        """

        signal.config.connect(self._callback_config)

    @asyncSlot()
    async def _callback_config(self, config: Config) -> None:
        """Callback of the configuration.

        Parameters
        ----------
        config : `Config`
            Configuration.
        """

        self._configuration["max_velocity_limit"].setText(
            f"{config.max_velocity_limit} deg/sec"
        )
        self._configuration["velocity_limit"].setText(
            f"{config.velocity_limit} deg/sec"
        )
        self._configuration["acceleration_limit"].setText(
            f"{config.accel_limit} deg/sec^2"
        )

        self._configuration["position_error_threshold"].setText(
            f"{config.pos_error_threshold} deg"
        )
        self._configuration["upper_position_limit"].setText(
            f"{config.upper_pos_limit} deg"
        )
        self._configuration["lower_position_limit"].setText(
            f"{config.lower_pos_limit} deg"
        )
        self._configuration["disable_limit_max_time"].setText(
            f"{config.disable_limit_max_time} sec"
        )

        self._configuration["following_error_threshold"].setText(
            f"{config.following_error_threshold} deg"
        )

        self._configuration["tracking_lost_timeout"].setText(
            f"{config.tracking_lost_timeout} sec"
        )
        self._configuration["tracking_success_threshold"].setText(
            f"{config.track_success_pos_threshold} deg"
        )

        self._configuration["emergency_jerk_limit"].setText(
            f"{config.emergency_jerk_limit} deg/sec^3"
        )
        self._configuration["emergency_acceleration_limit"].setText(
            f"{config.emergency_accel_limit} deg/sec^2"
        )

        color = Qt.green if config.drives_enabled else Qt.red
        self._configuration["drives_enabled"].setText(
            f"<font color='{color.name}'>{str(config.drives_enabled)}</font>"
        )
