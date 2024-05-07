from typing import Dict, List, Union

import numpy as np
import sdf_helper as sdfh
from sdf import BlockList

from epoch_toolkit.core import Component, EpochDataMapping, Grid, Unit
from epoch_toolkit.utils.logging import LogMixin

# ----------------------- #


class FileHandler(LogMixin):
    data: BlockList = None
    grid: Grid = None
    structure: Dict[EpochDataMapping, List[str]] = None

    # ....................... #

    def __init__(
        self,
        unit: Union[str, Unit] = None,
        verbose: bool = False,
        log_level: str = "info",
    ):
        super().__init__(logger_name="handler", log_level=log_level)

        if isinstance(unit, str):
            unit = Unit.get(unit)

        self.unit = unit
        self.verbose = verbose

    # ....................... #

    @property
    def time_fs(self):
        if self.data is not None:
            return self.data.Header["time"]

        else:
            raise ValueError("No data loaded")

    # ....................... #

    def _get(self, key: str):
        if hasattr(self.data, key):
            return getattr(self.data, key).data

        else:
            raise ValueError(f"Key not found: {key}")

    # ....................... #

    # def set_unit(self, unit: Union[str, Unit]):  # ? or as property ?#
    #     if isinstance(unit, str):
    #         unit = Unit.get(unit)

    #     self.unit = unit

    # ....................... #

    def read(self, path: str):
        self.info(f"Reading file: {path}")
        self.data = sdfh.getdata(path, verbose=self.verbose)

        self.info("Capturing grid...")
        self.grid = Grid.from_sdf(self.data)
        self.info(
            "Grid: %sD %s", self.grid.dim, tuple([x.size for x in self.grid.axes])
        )

    # ....................... #

    def analyze(self):
        all_keys = list(self.data.__dict__.keys())

        # TODO: analyze species, fields etc. and log them
        # ? record possible values into structure?

    # ....................... #

    def density(self, specie: str = None) -> np.ndarray:
        key = EpochDataMapping.density.value

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def temperature(self, specie: str = None) -> np.ndarray:
        key = EpochDataMapping.temperature.value

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def electric_field(self, component: Union[str, Component] = Component.x):
        if isinstance(component, str):
            component = Component.get(component)

        if component is Component.r:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.r3d:
            raise NotImplementedError("Spherical CS not implemented")

        elif component is Component.phi:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.theta:
            raise NotImplementedError("Spherical CS not implemented")

        else:
            if component is Component.y and self.grid.dim == 1:
                raise ValueError("Cannot calculate `y` for 1D grid")

            if component is Component.z and self.grid.dim < 3:
                raise ValueError("Cannot calculate `z` for 1D or 2D grid")

            key = f"{EpochDataMapping.electric_field.value}{component.value}"

            return self._get(key)

    # ....................... #

    def magnetic_field(self, component: Union[str, Component] = Component.x):
        if isinstance(component, str):
            component = Component.get(component)

        if component is Component.r:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.r3d:
            raise NotImplementedError("Spherical CS not implemented")

        elif component is Component.phi:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.theta:
            raise NotImplementedError("Spherical CS not implemented")

        else:
            if component is Component.y and self.grid.dim == 1:
                raise ValueError("Cannot calculate `y` for 1D grid")

            if component is Component.z and self.grid.dim < 3:
                raise ValueError("Cannot calculate `z` for 1D or 2D grid")

            key = f"{EpochDataMapping.magnetic_field.value}{component.value}"

            return self._get(key)

    # ....................... #

    def current(self, component: Union[str, Component] = Component.x):
        if isinstance(component, str):
            component = Component.get(component)

        if component is Component.r:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.r3d:
            raise NotImplementedError("Spherical CS not implemented")

        elif component is Component.phi:
            raise NotImplementedError("Cylindrical CS not implemented")

        elif component is Component.theta:
            raise NotImplementedError("Spherical CS not implemented")

        else:
            if component is Component.y and self.grid.dim == 1:
                raise ValueError("Cannot calculate `y` for 1D grid")

            if component is Component.z and self.grid.dim < 3:
                raise ValueError("Cannot calculate `z` for 1D or 2D grid")

            key = f"{EpochDataMapping.current.value}{component.value}"

            return self._get(key)

    # ....................... #

    def coordinates(self, specie: str):
        key = f"{EpochDataMapping.coordinates.value}_{specie}"

        return self._get(key)

    # ....................... #

    # TODO: add support for cylindrical and spherical CS
    # TODO: define abstract transformations for CS
    def momentum(self, specie: str, component: Union[str, Component] = Component.x):
        if isinstance(component, str):
            component = Component.get(component)

        if component is Component.r:
            if self.grid.dim < 3:
                raise ValueError("Cannot calculate `r` for 1D or 2D grid")

            py = self.momentum(specie, Component.y)
            pz = self.momentum(specie, Component.z)

            return np.sqrt(py**2 + pz**2)

        elif component is Component.r3d:
            raise NotImplementedError("Spherical CS not implemented")

        elif component is Component.phi:
            if self.grid.dim < 3:
                raise ValueError("Cannot calculate `r` for 1D or 2D grid")

            py = self.momentum(specie, Component.y)
            pz = self.momentum(specie, Component.z)

            return np.arctan2(pz, py)

        elif component is Component.theta:
            raise NotImplementedError("Spherical CS not implemented")

        else:
            if component is Component.y and self.grid.dim == 1:
                raise ValueError("Cannot calculate `y` for 1D grid")

            if component is Component.z and self.grid.dim < 3:
                raise ValueError("Cannot calculate `z` for 1D or 2D grid")

            key = f"{EpochDataMapping.momentum.value}{component.value}_{specie}"

            return self._get(key)
