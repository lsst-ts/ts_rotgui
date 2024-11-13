# This file is part of ts_rotgui.
#
# Developed for the LSST Telescope and Site Systems.
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

__all__ = ["ControlPanel"]

from lsst.ts.guitool import create_group_box, create_label, set_button
from lsst.ts.xml.enums import MTRotator
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from .constants import MAX_ROTATION, MAX_VELOCITY
from .enums import CommandSource, TriggerEnabledSubState, TriggerState
from .model import Model


class ControlPanel(QWidget):
    """Control panel.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide6.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model: Model) -> None:
        super().__init__()

        self.model = model

        self._indicator_fault = set_button(
            "",
            None,
            is_indicator=True,
            tool_tip="System is faulted or not.",
        )
        self._labels = {
            "source": create_label(),
            "state": create_label(),
            "enabled_substate": create_label(),
            "fault_substate": create_label(),
            "odometer": create_label(),
            "position": create_label(),
        }

        self._command_parameters = self._create_command_parameters()
        self._commands = self._create_commands()

        self._buttons = self._create_buttons()

        self.setLayout(self._create_layout())

        self._set_default()

    def _create_command_parameters(
        self,
        decimal_position: int = 2,
        decimal_velocity: int = 4,
    ) -> dict:
        """Create the command parameters.

        Parameters
        ----------
        decimal_position : `int`, optional
            Decimal of the position. (the default is 2)
        decimal_velocity : `int`, optional
            Decimal of the velocity. (the default is 4)

        Returns
        -------
        `dict`
            Command parameters.
        """

        state = QComboBox()
        for trigger in TriggerState:
            state.addItem(trigger.name)

        enabled_substate = QComboBox()
        for substate in TriggerEnabledSubState:
            enabled_substate.addItem(substate.name)

        position = QDoubleSpinBox()
        position.setDecimals(decimal_position)
        position.setRange(-MAX_ROTATION, MAX_ROTATION)
        position.setSuffix(" deg")
        position.setSingleStep(10**-decimal_position)

        velocity = QDoubleSpinBox()
        velocity.setDecimals(decimal_velocity)
        velocity.setRange(-MAX_VELOCITY, MAX_VELOCITY)
        velocity.setSuffix(" deg/sec")
        velocity.setSingleStep(10**-decimal_velocity)

        duration = QDoubleSpinBox()
        duration.setSuffix(" sec")

        return {
            "state": state,
            "enabled_substate": enabled_substate,
            "position": position,
            "velocity": velocity,
            "duration": duration,
        }

    def _create_commands(self) -> dict:
        """Create the commands.

        Returns
        -------
        `dict`
            Commands. The key is the name of the command and the value is the
            button.
        """

        command_state = QRadioButton("State command", parent=self)
        command_enabled_substate = QRadioButton(
            "Enabled Sub-State command", parent=self
        )
        command_position = QRadioButton("Position set command", parent=self)
        command_velocity = QRadioButton("Velocity set command", parent=self)

        command_state.setToolTip("Transition the state.")
        command_enabled_substate.setToolTip("Transition the enabled sub-state.")
        command_position.setToolTip("Set the position in point-to-point movement.")
        command_velocity.setToolTip(
            "Set the velocity used in the constant velocity movement."
        )

        command_state.toggled.connect(self._callback_command)
        command_enabled_substate.toggled.connect(self._callback_command)
        command_position.toggled.connect(self._callback_command)
        command_velocity.toggled.connect(self._callback_command)

        return {
            "state": command_state,
            "enabled_substate": command_enabled_substate,
            "position": command_position,
            "velocity": command_velocity,
        }

    @asyncSlot()
    async def _callback_command(self) -> None:
        """Callback of the command button."""

        if self._commands["state"].isChecked():
            self._enable_command_parameters(["state"])

        elif self._commands["enabled_substate"].isChecked():
            self._enable_command_parameters(["enabled_substate"])

        elif self._commands["position"].isChecked():
            self._enable_command_parameters(["position"])

        elif self._commands["velocity"].isChecked():
            self._enable_command_parameters(["velocity", "duration"])

    def _enable_command_parameters(self, enabled_parameters: list[str]) -> None:
        """Enable the command parameters.

        Parameters
        ----------
        enabled_parameters : `list` [`str`]
            Enabled command parameters.
        """

        for name, value in self._command_parameters.items():
            value.setEnabled(name in enabled_parameters)

    def _create_buttons(self) -> dict:
        """Create the buttons.

        Returns
        -------
        `dict`
            Buttons. The key is the name of the button and the value is the
            button.
        """

        send_command = set_button(
            "Send Command",
            self._callback_send_command,
            tool_tip="Send the command to the controller.",
        )

        switch_commander = set_button(
            "Switch Command Source",
            self._callback_switch_commander,
            tool_tip="Switch the command source (GUI or CSC).",
        )

        mask_limit_switch = set_button(
            "Mask Limit Switch",
            self._callback_mask_limit_switch,
            tool_tip="Temporarily mask the limit switches.",
        )

        log_telemetry = set_button(
            "Log Telemetry",
            self._callback_log_telemetry,
            is_checkable=True,
            tool_tip="Log the telemetry.",
        )

        return {
            "send_command": send_command,
            "switch_commander": switch_commander,
            "mask_limit_switch": mask_limit_switch,
            "log_telemetry": log_telemetry,
        }

    @asyncSlot()
    async def _callback_send_command(self) -> None:
        """Callback of the send-command button to command the controller."""

        self.model.log.info("Send the command.")

    @asyncSlot()
    async def _callback_switch_commander(self) -> None:
        """Callback of the switch-commander button to switch the commander."""

        self.model.log.info("Switch the command source.")

    @asyncSlot()
    async def _callback_mask_limit_switch(self) -> None:
        """Callback of the mask-limit-switch button to mask the limit
        switches."""

        self.model.log.info("Mask the limit switches.")

    @asyncSlot()
    async def _callback_log_telemetry(self) -> None:
        """Callback of the log-telemetry button to log the telemetry."""

        if self._buttons["log_telemetry"].isChecked():
            self.model.log.info("Log the telemetry.")
        else:
            self.model.log.info("Stop logging the telemetry.")

    def _create_layout(self) -> QVBoxLayout:
        """Set the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_summary())
        layout.addWidget(self._create_group_commands())
        layout.addWidget(self._create_group_special_commands())

        return layout

    def _create_group_summary(self) -> QGroupBox:
        """Create the group of summary.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Fault Status:", self._indicator_fault)
        layout.addRow("Command Source:", self._labels["source"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("State:", self._labels["state"])
        layout.addRow("Enabled Sub-State:", self._labels["enabled_substate"])
        layout.addRow("Fault Sub-State:", self._labels["fault_substate"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Odometer (deg):", self._labels["odometer"])
        layout.addRow("Position (deg):", self._labels["position"])

        return create_group_box("Summary", layout)

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def _create_group_commands(self) -> QGroupBox:
        """Create the group of commands.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_commands = QHBoxLayout()
        layout_commands.addWidget(self._create_group_command_name())
        layout_commands.addWidget(self._create_group_command_parameters())

        layout = QVBoxLayout()
        layout.addLayout(layout_commands)
        layout.addWidget(self._buttons["send_command"])

        return create_group_box("Commands", layout)

    def _create_group_command_name(self) -> QGroupBox:
        """Create the group of command name.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        for command in self._commands.values():
            layout.addWidget(command)

        return create_group_box("Command", layout)

    def _create_group_command_parameters(self) -> QGroupBox:
        """Create the group of command parameters.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_parameters = QFormLayout()
        layout_parameters.addRow("State Trigger", self._command_parameters["state"])
        layout_parameters.addRow(
            "Enabled Sub-State Trigger", self._command_parameters["enabled_substate"]
        )
        layout_parameters.addRow("Position", self._command_parameters["position"])
        layout_parameters.addRow("Velocity", self._command_parameters["velocity"])
        layout_parameters.addRow("Duration", self._command_parameters["duration"])

        layout = QVBoxLayout()
        layout.addLayout(layout_parameters)

        return create_group_box("Command Parameters", layout)

    def _create_group_special_commands(self) -> QGroupBox:
        """Create the group of special commands.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._buttons["switch_commander"])
        layout.addWidget(self._buttons["mask_limit_switch"])
        layout.addWidget(self._buttons["log_telemetry"])

        return create_group_box("Special Commands", layout)

    def _set_default(self) -> None:
        """Set the default values."""

        self._update_fault_status(False)

        self._labels["source"].setText(CommandSource.GUI.name)

        self._labels["state"].setText(MTRotator.ControllerState.STANDBY.name)
        self._labels["enabled_substate"].setText(
            MTRotator.EnabledSubstate.STATIONARY.name
        )
        self._labels["fault_substate"].setText(MTRotator.FaultSubstate.NO_ERROR.name)

        self._labels["odometer"].setText("0")
        self._labels["position"].setText("0")

        self._commands["state"].setChecked(True)

    def _update_fault_status(self, is_fault: bool) -> None:
        """Update the fault status.

        Parameters
        ----------
        is_fault : `bool`
            Is fault or not.
        """

        # Set the text
        text = "Faulted" if is_fault else "Not Faulted"
        self._indicator_fault.setText(text)

        # Set the color
        palette = self._indicator_fault.palette()

        color = Qt.red if is_fault else Qt.green
        palette.setColor(QPalette.Button, color)

        self._indicator_fault.setPalette(palette)
