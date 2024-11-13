"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

import lsst.ts.rotgui  # type: ignore # noqa
from documenteer.conf.pipelinespkg import *  # type: ignore # noqa

project = "ts_rotgui"
html_theme_options["logotext"] = project  # type: ignore # noqa
html_title = project
html_short_title = project
doxylink = {}  # type: ignore # noqa

# Support the sphinx extension of mermaid
extensions = [
    "sphinxcontrib.mermaid",
    "sphinx_automodapi.automodapi",
]
