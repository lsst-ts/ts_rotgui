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

__all__ = ["ControlPanel"]

from lsst.ts.guitool import (
    ButtonStatus,
    create_double_spin_box,
    create_group_box,
    create_label,
    set_button,
    update_button_color,
)
from lsst.ts.xml.enums import MTRotator
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QComboBox,
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
from .signals import SignalPositionVelocity, SignalState


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

        self._set_signal_state(self.model.signals["state"])  # type: ignore[arg-type]
        self._set_signal_position_velocity(self.model.signals["position_velocity"])  # type: ignore[arg-type]

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

        position = create_double_spin_box(
            "deg",
            decimal_position,
            maximum=MAX_ROTATION,
            minimum=-MAX_ROTATION,
        )

        velocity = create_double_spin_box(
            "deg/sec",
            decimal_velocity,
            maximum=MAX_VELOCITY,
            minimum=-MAX_VELOCITY,
        )

        duration = create_double_spin_box("sec", 1)

        command_source = QComboBox()
        for source in CommandSource:
            command_source.addItem(source.name)

        return {
            "state": state,
            "enabled_substate": enabled_substate,
            "position": position,
            "velocity": velocity,
            "duration": duration,
            "source": command_source,
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
            "Enabled sub-state command", parent=self
        )
        command_position = QRadioButton("Position set command", parent=self)
        command_velocity = QRadioButton("Velocity set command", parent=self)
        command_commander = QRadioButton("Switch command source", parent=self)
        command_mask = QRadioButton("Mask limit switch", parent=self)
        command_disable_upper = QRadioButton(
            "Disable upper position limit", parent=self
        )
        command_disable_lower = QRadioButton(
            "Disable lower position limit", parent=self
        )

        command_state.setToolTip("Transition the state.")
        command_enabled_substate.setToolTip("Transition the enabled sub-state.")
        command_position.setToolTip("Set the position in point-to-point movement.")
        command_velocity.setToolTip(
            "Set the velocity used in the constant velocity movement."
        )
        command_commander.setToolTip("Switch the command source (GUI or CSC).")
        command_mask.setToolTip("Temporarily mask the limit switches.")
        command_disable_upper.setToolTip("Disable the upper position limit.")
        command_disable_lower.setToolTip("Disable the lower position limit.")

        command_state.toggled.connect(self._callback_command)
        command_enabled_substate.toggled.connect(self._callback_command)
        command_position.toggled.connect(self._callback_command)
        command_velocity.toggled.connect(self._callback_command)
        command_commander.toggled.connect(self._callback_command)
        command_mask.toggled.connect(self._callback_command)
        command_disable_upper.toggled.connect(self._callback_command)
        command_disable_lower.toggled.connect(self._callback_command)

        return {
            "state": command_state,
            "enabled_substate": command_enabled_substate,
            "position": command_position,
            "velocity": command_velocity,
            "commander": command_commander,
            "mask": command_mask,
            "disable_upper": command_disable_upper,
            "disable_lower": command_disable_lower,
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

        elif self._commands["commander"].isChecked():
            self._enable_command_parameters(["source"])

        elif self._commands["mask"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["disable_upper"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["disable_lower"].isChecked():
            self._enable_command_parameters([])

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

        log_telemetry = set_button(
            "Log Telemetry",
            self._callback_log_telemetry,
            is_checkable=True,
            tool_tip="Log the telemetry.",
        )

        return {
            "send_command": send_command,
            "log_telemetry": log_telemetry,
        }

    @asyncSlot()
    async def _callback_send_command(self) -> None:
        """Callback of the send-command button to command the controller."""

        self.model.log.info("Send the command.")

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
        layout_parameters.addRow("State trigger:", self._command_parameters["state"])
        layout_parameters.addRow(
            "Enabled sub-state trigger:", self._command_parameters["enabled_substate"]
        )
        layout_parameters.addRow("Position:", self._command_parameters["position"])
        layout_parameters.addRow("Velocity:", self._command_parameters["velocity"])
        layout_parameters.addRow("Duration:", self._command_parameters["duration"])
        layout_parameters.addRow("Command source:", self._command_parameters["source"])

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
        layout.addWidget(self._buttons["log_telemetry"])

        return create_group_box("Special Command", layout)

    def _set_signal_state(self, signal: SignalState) -> None:
        """Set the state signal.

        Parameters
        ----------
        signal : `SignalState`
            Signal.
        """

        signal.command_source.connect(self._callback_command_source)
        signal.state.connect(self._callback_state)
        signal.substate_enabled.connect(self._callback_substate_enabled)
        signal.substate_fault.connect(self._callback_substate_fault)

    @asyncSlot()
    async def _callback_command_source(self, source: int) -> None:
        """Callback of the controller's command source signal.

        Parameters
        ----------
        source : `int`
            Source.
        """

        self._labels["source"].setText(CommandSource(source).name)

    @asyncSlot()
    async def _callback_state(self, state: int) -> None:
        """Callback of the controller's state signal.

        Parameters
        ----------
        state : `int`
            State.
        """

        controller_state = MTRotator.ControllerState(state)
        self._labels["state"].setText(controller_state.name)

        self._update_fault_status(controller_state == MTRotator.ControllerState.FAULT)

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
        status = ButtonStatus.Error if is_fault else ButtonStatus.Normal
        update_button_color(self._indicator_fault, QPalette.Button, status)

    @asyncSlot()
    async def _callback_substate_enabled(self, substate: int) -> None:
        """Callback of the controller's enabled substate signal.

        Parameters
        ----------
        substate : `int`
            Substate.
        """

        self._labels["enabled_substate"].setText(
            MTRotator.EnabledSubstate(substate).name
        )

    @asyncSlot()
    async def _callback_substate_fault(self, substate: int) -> None:
        """Callback of the controller's fault substate signal.

        Parameters
        ----------
        substate : `int`
            Substate.
        """

        self._labels["fault_substate"].setText(MTRotator.FaultSubstate(substate).name)

    def _set_signal_position_velocity(self, signal: SignalPositionVelocity) -> None:
        """Set the position-velocity signal.

        Parameters
        ----------
        signal : `SignalPositionVelocity`
            Signal.
        """

        signal.position_current.connect(self._callback_position_current)
        signal.odometer.connect(self._callback_odometer)

    @asyncSlot()
    async def _callback_position_current(self, position: float) -> None:
        """Callback of the current position.

        Parameters
        ----------
        position : `float`
            Position in deg.
        """

        self._labels["position"].setText(f"{position:.7f}")

    @asyncSlot()
    async def _callback_odometer(self, odometer: float) -> None:
        """Callback of the odometer.

        Parameters
        ----------
        odometer : `float`
            Odometer in deg.
        """

        self._labels["odometer"].setText(f"{odometer:.7f}")

    def _set_default(self) -> None:
        """Set the default."""

        self._commands["state"].setChecked(True)
