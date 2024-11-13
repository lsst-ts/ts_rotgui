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

__all__ = ["TabSettings"]

from lsst.ts.guitool import (
    LOG_LEVEL_MAXIMUM,
    LOG_LEVEL_MINIMUM,
    POINT_SIZE_MAXIMUM,
    POINT_SIZE_MINIMUM,
    PORT_MAXIMUM,
    PORT_MINIMUM,
    REFRESH_FREQUENCY_MAXIMUM,
    REFRESH_FREQUENCY_MINIMUM,
    TIMEOUT_MINIMUM,
    TabTemplate,
    create_group_box,
    set_button,
)
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLineEdit, QSpinBox, QVBoxLayout
from qasync import QApplication, asyncSlot

from ..model import Model


class TabSettings(TabTemplate):
    """Table of the settings.

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

        self._settings = self._create_settings()
        self._buttons = self._create_buttons()

        self.set_widget_and_layout()

    def _create_settings(self) -> dict:
        """Create the settings.

        Returns
        -------
        `dict`
            Settings.
        """

        settings = {
            "host": QLineEdit(),
            "port": QSpinBox(),
            "timeout_connection": QSpinBox(),
            "log_level": QSpinBox(),
            "refresh_frequency": QSpinBox(),
            "point_size": QSpinBox(),
        }

        settings["port"].setRange(PORT_MINIMUM, PORT_MAXIMUM)

        settings["timeout_connection"].setMinimum(TIMEOUT_MINIMUM)
        settings["timeout_connection"].setSuffix(" sec")

        settings["log_level"].setRange(LOG_LEVEL_MINIMUM, LOG_LEVEL_MAXIMUM)
        settings["log_level"].setToolTip(
            "CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10)"
        )

        settings["refresh_frequency"].setRange(
            REFRESH_FREQUENCY_MINIMUM, REFRESH_FREQUENCY_MAXIMUM
        )
        settings["refresh_frequency"].setSuffix(" Hz")
        settings["refresh_frequency"].setToolTip(
            "Frequency to refresh the data on tables"
        )

        settings["point_size"].setRange(POINT_SIZE_MINIMUM, POINT_SIZE_MAXIMUM)
        settings["point_size"].setToolTip("Point size of the application.")

        # Set the default values
        connection_information = self.model.connection_information
        settings["host"].setText(connection_information["host"])
        settings["port"].setValue(connection_information["port"])
        settings["timeout_connection"].setValue(
            connection_information["timeout_connection"]
        )

        settings["log_level"].setValue(self.model.log.level)

        # The unit of self.model.duration_refresh is milliseconds
        frequency = int(1000 / self.model.duration_refresh)
        settings["refresh_frequency"].setValue(frequency)

        app = QApplication.instance()
        settings["point_size"].setValue(app.font().pointSize())

        self._set_minimum_width_line_edit(settings["host"])

        return settings

    def _set_minimum_width_line_edit(
        self, line_edit: QLineEdit, offset: int = 20
    ) -> None:
        """Set the minimum width of line edit.

        Parameters
        ----------
        line_edit : `PySide6.QtWidgets.QLineEdit`
            Line edit.
        offset : `int`, optional
            Offset of the width. (the default is 20)
        """

        font_metrics = line_edit.fontMetrics()

        text = line_edit.text()
        width = font_metrics.boundingRect(text).width()
        line_edit.setMinimumWidth(width + offset)

    def _create_buttons(self) -> dict:
        """Create the buttons.

        Returns
        -------
        `dict`
            Buttons. The keys are the names of the buttons and the values are
            the buttons.
        """

        apply_host = set_button("Apply Host Settings", self._callback_apply_host)
        apply_general = set_button(
            "Apply General Settings", self._callback_apply_general
        )

        return {
            "apply_host": apply_host,
            "apply_general": apply_general,
        }

    @asyncSlot()
    async def _callback_apply_host(self) -> None:
        """Callback of the apply-host-setting button. This will apply the
        new host settings to model."""

        connection_information = self.model.connection_information
        connection_information["host"] = self._settings["host"].text()
        connection_information["port"] = self._settings["port"].value()
        connection_information["timeout_connection"] = self._settings[
            "timeout_connection"
        ].value()

    @asyncSlot()
    async def _callback_apply_general(self) -> None:
        """Callback of the apply-general-settings button. This will apply the
        new general settings to model."""

        self.model.log.setLevel(self._settings["log_level"].value())

        # The unit of self.model.duration_refresh is milliseconds
        self.model.duration_refresh = int(
            1000 / self._settings["refresh_frequency"].value()
        )

        # Update the point size
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(self._settings["point_size"].value())
        app.setFont(font)

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        layout.addWidget(self._create_group_tcpip())
        layout.addWidget(self._create_group_application())

        return layout

    def _create_group_tcpip(self) -> QGroupBox:
        """Create the group of TCP/IP connection.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_tcpip = QFormLayout()
        layout_tcpip.addRow("Host name:", self._settings["host"])
        layout_tcpip.addRow("Port:", self._settings["port"])
        layout_tcpip.addRow("Connection timeout:", self._settings["timeout_connection"])

        layout.addLayout(layout_tcpip)
        layout.addWidget(self._buttons["apply_host"])

        return create_group_box("Tcp/Ip Connection", layout)

    def _create_group_application(self) -> QGroupBox:
        """Create the group of application.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_app = QFormLayout()
        layout_app.addRow("Point size:", self._settings["point_size"])
        layout_app.addRow("Logging level:", self._settings["log_level"])
        layout_app.addRow("Refresh frequency:", self._settings["refresh_frequency"])

        layout.addLayout(layout_app)
        layout.addWidget(self._buttons["apply_general"])

        return create_group_box("Application", layout)
