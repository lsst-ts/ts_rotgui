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

__all__ = ["TabTarget"]


from lsst.ts.guitool import (
    create_table,
    create_group_box,
    create_double_spin_box,
    set_button,
    TabTemplate,
    prompt_dialog_warning,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
)
from qasync import asyncSlot

from ..constants import MAX_ROTATION, MAX_VELOCITY
from ..model import Model


class TabTarget(TabTemplate):
    """Widget containing QTableWidget with buttons to add and remove tracking
    targets (position, velocity, duration).

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

        # Table of the target
        self._table_target = self._create_table_target()

        # Controls to create the target
        self._target_parameters = self._create_target_parameters()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

    def _create_table_target(self) -> QTableWidget:
        """Create the tracking target's table widget.

        Returns
        -------
        table : `PySide6.QtWidgets.QTableWidget`
            Table widget.
        """

        header_text = ["Position (deg)", "Velocity (deg/s)", "Duration (s)"]
        table = create_table(header_text)
        table.verticalHeader().hide()

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        return table

    def _create_target_parameters(self) -> dict[str, QDoubleSpinBox]:
        """Create the target parameters.

        Returns
        -------
        `dict` [`str`, `PySide6.QtWidgets.QDoubleSpinBox`]
            Target parameters.
        """

        decimal_position = 2
        position = create_double_spin_box(
            "deg",
            decimal_position,
            maximum=MAX_ROTATION,
            minimum=-MAX_ROTATION,
        )

        decimal_velocity = 4
        velocity = create_double_spin_box(
            "deg/sec",
            decimal_velocity,
            maximum=MAX_VELOCITY,
            minimum=-MAX_VELOCITY,
        )

        decimal_duration = 1
        duration = create_double_spin_box("sec", decimal_duration)

        return {
            "position": position,
            "velocity": velocity,
            "duration": duration,
        }

    def _create_buttons(self) -> dict[str, QPushButton]:
        """Create the buttons.

        Returns
        -------
        buttons : `dict` [`str`, `PySide6.QtWidgets.QPushButton`]
            Buttons.
        """

        button_add = set_button("Add Target", self._callback_add_target, tool_tip="Add a new target.")
        button_remove = set_button(
            "Remove Target", self._callback_remove_target, tool_tip="Remove the selected target."
        )
        button_clear = set_button(
            "Clear Targets", self._callback_clear_targets, tool_tip="Clear all targets."
        )

        buttons = {
            "add": button_add,
            "remove": button_remove,
            "clear": button_clear,
        }

        return buttons

    @asyncSlot()
    async def _callback_add_target(self, is_prompted: bool = True) -> None:
        """Callback to add a new target.

        Parameters
        ----------
        is_prompted : `bool`, optional
            When False, dialog will not be executed. That is used for tests,
            which shall not be the case when used in the real GUI. (the default
            is True)
        """

        # Check the duration should be >0
        duration = self._target_parameters["duration"].value()
        function_name = "_callback_add_target()"
        if duration <= 0:
            await prompt_dialog_warning(
                function_name,
                "Duration must be greater than zero.",
                is_prompted=is_prompted,
            )

            return

        # Check the velocity should be !=0
        velocity = self._target_parameters["velocity"].value()
        if velocity == 0:
            await prompt_dialog_warning(
                function_name,
                "Velocity should not equal zero.",
                is_prompted=is_prompted,
            )

            return

        # Add the target to the table
        row_count = self._table_target.rowCount()
        self._table_target.setRowCount(row_count + 1)

        position = self._target_parameters["position"].value()
        self._table_target.setItem(row_count, 0, self._create_non_editable_item(position))
        self._table_target.setItem(row_count, 1, self._create_non_editable_item(velocity))
        self._table_target.setItem(row_count, 2, self._create_non_editable_item(duration))

    def _create_non_editable_item(self, value: float) -> QTableWidgetItem:
        """Create a non-editable table item.

        Parameters
        ----------
        value : `float`
            Value of the item.

        Returns
        -------
        item : `PySide6.QtWidgets.QTableWidgetItem`
            Table item.
        """

        item = QTableWidgetItem(str(value))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    @asyncSlot()
    async def _callback_remove_target(self) -> None:
        """Callback to remove the selected target."""

        # When removing the items, remove from the bottom to the top to avoid
        # index shifting.
        items = self._table_target.selectedItems()
        rows = sorted(set(item.row() for item in items), reverse=True)
        for row in rows:
            self._table_target.removeRow(row)

    @asyncSlot()
    async def _callback_clear_targets(self) -> None:
        """Callback to clear all targets."""

        self._table_target.setRowCount(0)

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._table_target)
        layout.addWidget(self._create_group_target_parameters())
        layout.addWidget(self._create_group_target_control())

        return layout

    def _create_group_target_parameters(self) -> QGroupBox:
        """Create the group of target parameters.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_form = QFormLayout()
        layout_form.addRow("Position:", self._target_parameters["position"])
        layout_form.addRow("Velocity:", self._target_parameters["velocity"])
        layout_form.addRow("Duration:", self._target_parameters["duration"])

        layout = QVBoxLayout()
        layout.addLayout(layout_form)

        return create_group_box("Target Parameters", layout)

    def _create_group_target_control(self) -> QGroupBox:
        """Create the group of target control.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QHBoxLayout()
        for button in self._buttons.values():
            layout.addWidget(button)

        return create_group_box("Add/Remove Target", layout)

    def get_targets(self) -> list[list[float]]:
        """Get the tracking targets from the table.

        Returns
        -------
        targets : `list` [`list`]
            List of targets: [position, velocity, duration]. The unit of
            position is degrees, velocity is degrees/second, and duration is
            seconds.
        """

        targets = list()
        row_count = self._table_target.rowCount()
        column_count = self._table_target.columnCount()
        for row in range(row_count):
            target = list()
            for column in range(column_count):
                item = self._table_target.item(row, column)
                target.append(float(item.text()))

            targets.append(target)

        return targets
