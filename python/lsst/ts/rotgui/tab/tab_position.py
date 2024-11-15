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

__all__ = ["TabPosition"]

from lsst.ts.guitool import FigureConstant, TabTemplate
from PySide6.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..model import Model


class TabPosition(TabTemplate):
    """Table of the rotator position.

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

    MIN_WIDTH = 150

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title)

        # In degree
        self._position = 0.0

        # In degree per second
        self._velocity = 0.0

        # Realtime figures
        self._figures = self._create_figures()

        self.model = model

        # Timer to update the realtime figures
        self._timer = self.create_and_start_timer(
            self._callback_time_out, self.model.duration_refresh
        )

        self.set_widget_and_layout()

    def _create_figures(self, num_realtime: int = 200) -> dict:
        """Create the figures to show the position and velocity.

        Parameters
        ----------
        num_realtime : `int`, optional
            Number of the realtime data (>=0). (the default is 200)

        Returns
        -------
        figures : `dict`
            Figures of the position and velocity.
        """

        figures = dict()
        axes = ["position", "velocity"]
        y_labels = ["Position (deg)", "Velocity (deg/sec)"]
        for axis, y_label in zip(axes, y_labels):
            figures[axis] = FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                y_label,
                axis,
                legends=[],
                num_lines=1,
                is_realtime=True,
            )

        for figure in figures.values():
            figure.axis_x.setLabelFormat("%d")

        return figures

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the realtime figures."""

        self._figures["position"].append_data(self._position)
        self._figures["velocity"].append_data(self._velocity)

        self.check_duration_and_restart_timer(self._timer, self.model.duration_refresh)

    def create_layout(self) -> QVBoxLayout:

        layout = QVBoxLayout()
        for figure in self._figures.values():
            figure.setMinimumWidth(self.MIN_WIDTH)
            layout.addWidget(figure)

        return layout
