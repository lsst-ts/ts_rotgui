# Rotator Graphical User Interface (GUI) in Python

## Platform

- AlmaLinux 8.10
- python: 3.11.9

## Needed Package

- numpy (install by `conda`)
- pyyaml (install by `conda`)
- pyside6 (install by `conda`)
- qt6-charts (install by `conda`)
- qt5-qtbase-devel (install by `dnf`)
- xorg-x11-server-Xvfb (optional, install by `dnf`)
- qasync (install by `conda -c conda-forge`)
- [black](https://github.com/psf/black) (optional)
- [flake8](https://github.com/PyCQA/flake8) (optional)
- [isort](https://github.com/PyCQA/isort) (optional)
- [mypy](https://github.com/python/mypy) (optional)
- [documenteer](https://github.com/lsst-sqre/documenteer) (optional)
- pytest (optional, install by `conda`)
- pytest-flake8 (optional, install by `conda -c conda-forge`)
- pytest-qt (optional, install by `conda -c conda-forge`)
- pytest-xvfb (optional, install by `conda -c conda-forge`)

## Code Format

This code is automatically formatted by `black` using a git pre-commit hook (see `.pre-commit-config.yaml`), which comes from the `.ts_pre_commit_config.yaml`.

To enable this, see [pre-commit](https://pre-commit.com).

## Build the Document

To build project documentation, run `package-docs build` to build the documentation.
To clean the built documents, use `package-docs clean`.
See [Building single-package documentation locally](https://developer.lsst.io/stack/building-single-package-docs.html) for further details.

## Run GUI in Docker Container

You need to set the QT environment variables:

```bash
export QT_API="PySide6"
export PYTEST_QT_API="PySide6"
```

### AlmaLinux

If the user of docker container has no writing permission to the X11 socket, you need to run the following command first (use the `root` user in container):

```bash
xhost local:root
```

Then, do the image forwarding by the following command (note you need to use the `root` as the user or not):

```bash
docker run -it --rm -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ${path_to_this_package}:${path_of_package_in_container} ${docker_image}:${image_tag}
```

### MacOS

1. Setup the x11 by following: [x11_docker_mac](https://gist.github.com/cschiewek/246a244ba23da8b9f0e7b11a68bf3285).

2. Forward GUI by (note the MacOS will handle the writing permission for you):

```bash
xhost +
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
docker run -it --rm -e DISPLAY=${IP}:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v ${path_to_this_package}:${path_of_package_in_container} ${docker_image}:${image_tag}
```

## Run GUI without the LSST Docker Image on MacOS

You need to setup the QT environment with:

```bash
export QT_MAC_WANTS_LAYER=1
export QT_MAC_USE_NSWINDOW=1
```

You may need to setup the **PYTHONPATH** to point to `python/` directory as well.

## Executable

The executable (`run_rotgui`) is under the `bin/` directory.
Use the argument of `-h` to know the available options.
The logged message will be under the `log/` directory.

## Unit Tests

You can run the unit tests by:

```bash
pytest tests/
```

If you have the **Xvfb** and **pytest-xvfb** installed, you will not see the prompted windows when running the unit tests.

Note: If the variable of `PYTEST_QT_API` is not set, you might get the core dump error in the test.

## Class Diagrams

The class diagrams are in [here](doc/uml).
You can use the [Mermaid](https://mermaid.live) to read them.
QT is an event-based framework and the signal plays an important role among classes.
The `emit()` and `connect()` in the class diagrams mean the class **emits** a specific siganl or **connects** it to a specific callback function.
