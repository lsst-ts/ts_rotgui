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

__all__ = ["MainWindow"]

import logging
import pathlib
import sys
from datetime import datetime

from lsst.ts.guitool import ControlTabs, QMessageBoxAsync, get_button_action
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QToolBar, QVBoxLayout, QWidget
from qasync import QApplication, asyncSlot

from .control_panel import ControlPanel
from .model import Model
from .tab import TabDriveStatus, TabPosition, TabSettings, TabTelemetry


class MainWindow(QMainWindow):
    """Main window of the application.

    Parameters
    ----------
    is_output_log_to_file : `bool`
        Is outputting the log messages to file or not.
    is_output_log_on_screen : `bool`
        Is outputting the log messages on screen or not.
    is_simulation_mode: `bool`
        Is the simulation mode or not.
    log : `logging.Logger` or None, optional
        A logger. If None, a logger will be instantiated. (the default is
        None)
    log_level : `int`, optional
        Logging level. (the default is `logging.WARN`)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    model : `Model`
        Model class.
    """

    def __init__(
        self,
        is_output_log_to_file: bool,
        is_output_log_on_screen: bool,
        is_simulation_mode: bool,
        log: logging.Logger | None = None,
        log_level: int = logging.WARN,
    ) -> None:
        super().__init__()

        # Set the logger
        message_format = "%(asctime)s, %(levelname)s, %(message)s"
        self.log = self._set_log(
            message_format,
            is_output_log_to_file,
            is_output_log_on_screen,
            log_level,
            log=log,
        )

        self.model = Model(
            self.log,
            is_simulation_mode=is_simulation_mode,
        )
        self._control_panel = ControlPanel(self.model)

        # Control tabs
        tabs = [
            TabTelemetry("Telemetry", self.model),
            TabDriveStatus("Drive Status (Axis A+B)", self.model),
            TabPosition("Position", self.model),
        ]
        self._control_tabs = ControlTabs(tabs)

        # Table to have the settings
        self._tab_settings = TabSettings("Settings", self.model)

        # Set the main window of application
        self.setWindowTitle("Rotator Control")

        # Set the central widget of the Window
        container = QWidget()
        container.setLayout(self._create_layout())
        self.setCentralWidget(container)

        # Disable the Qt close button
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
        )

        self._add_tool_bar()

        if is_simulation_mode:
            self.log.info("Running the simulation mode.")

    def _set_log(
        self,
        message_format: str,
        is_output_log_to_file: bool,
        is_output_log_on_screen: bool,
        level: int,
        log: logging.Logger | None = None,
    ) -> logging.Logger:
        """Set the logger.

        Parameters
        ----------
        message_format : `str`
            Format of the message.
        is_output_log_to_file : `bool`
            Is outputting the log messages to file or not.
        is_output_log_on_screen : `bool`
            Is outputting the log messages on screen or not.
        level : `int`
            Logging level.
        log : `logging.Logger` or None, optional
            A logger. If None, a logger will be instantiated. (the default is
            None)

        Returns
        -------
        log : `logging.Logger`
            A logger.
        """

        if log is None:
            log = logging.getLogger(type(self).__name__)
        else:
            log = log.getChild(type(self).__name__)

        if is_output_log_to_file:
            logging.basicConfig(
                filename=self._get_log_file_name(),
                format=message_format,
            )
        else:
            logging.basicConfig(
                format=message_format,
            )

        if is_output_log_on_screen:
            log.addHandler(logging.StreamHandler(sys.stdout))

        log.setLevel(level)

        return log

    def _get_log_file_name(
        self, default_log_dir: str = "/rubin/rotator/log"
    ) -> pathlib.Path:
        """Get the log file name.

        Parameters
        ----------
        default_log_dir : `str`, optional
            Default log directory. (the default is "/rubin/rotator/log")

        Returns
        -------
        `pathlib.Path`
            Log file name.
        """

        log_dir = pathlib.Path(default_log_dir)
        if not log_dir.is_dir():
            print(
                (
                    f"Default log directory: {default_log_dir} does not exist. "
                    "Use the home directory instead."
                )
            )
            log_dir = pathlib.Path.home()

        name = "log_%s.txt" % datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

        return log_dir / name

    def _create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._control_panel)
        layout.addLayout(self._control_tabs.layout)

        return layout

    def _add_tool_bar(self) -> None:
        """Add the tool bar."""

        tool_bar = self.addToolBar("ToolBar")

        action_exit = tool_bar.addAction("Exit", self._callback_exit)
        action_exit.setToolTip("Exit the application (this might take some time)")

        action_connect = tool_bar.addAction("Connect", self._callback_connect)
        action_connect.setToolTip("Connect to the rotator controller")

        action_disconnect = tool_bar.addAction("Disconnect", self._callback_disconnect)
        action_disconnect.setToolTip(
            "Disconnect and close all tasks (this might take some time)"
        )

        action_settings = tool_bar.addAction("Settings", self._callback_settings)
        action_settings.setToolTip("Show the application settings")

    @asyncSlot()
    async def _callback_exit(self) -> None:
        """Exit the application.

        The 'exit' action will be disabled during the call. If the user cancels
        the exit (in the displayed message box), it will be reenabled.
        """

        action_exit = self._get_action("Exit")
        action_exit.setEnabled(False)

        dialog = self._create_dialog_exit()
        result = await dialog.show()

        if result == QMessageBoxAsync.Ok:
            QApplication.instance().quit()

        action_exit.setEnabled(True)

    def _get_action(self, name: str) -> QAction:
        """Get the action.

        Parameters
        ----------
        name : `str`
            Action name.

        Returns
        -------
        `PySide6.QtWidgets.QAction`
            Action.
        """

        tool_bar = self.findChildren(QToolBar)[0]
        return get_button_action(tool_bar, name)

    def _create_dialog_exit(self) -> QMessageBoxAsync:
        """Create the exit dialog.

        Returns
        -------
        dialog : `QMessageBoxAsync`
            Exit dialog.
        """

        dialog = QMessageBoxAsync()
        dialog.setIcon(QMessageBoxAsync.Warning)
        dialog.setWindowTitle("exit")

        dialog.setText("Exit the application?")
        dialog.addButton(QMessageBoxAsync.Ok)

        dialog.addButton(QMessageBoxAsync.Cancel)

        # Block the user to interact with other running widgets
        dialog.setModal(True)

        return dialog

    @asyncSlot()
    async def _callback_connect(self) -> None:
        """Callback function to connect to the controller."""

        self.log.info("Connect to the controller.")

    @asyncSlot()
    async def _callback_disconnect(self) -> None:
        """Callback function to disconnect from the controller."""

        self.log.info("Disconnect from the controller.")

    @asyncSlot()
    async def _callback_settings(self) -> None:
        """Callback function to show the settings."""

        self._tab_settings.show()
