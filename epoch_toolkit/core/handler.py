from typing import Union

import numpy as np
import sdf_helper as sdfh
from sdf import BlockList

from ..utils.logging import LogMixin
from .const import Component, Unit
from .grid import AbstractGrid, grid_factory

# ----------------------- #


class SingleFile(LogMixin):
    data: BlockList = None
    grid: AbstractGrid = None

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

    def read(self, path: str):
        self.info(f"Reading file: {path}")
        self.data = sdfh.getdata(path, verbose=self.verbose)

        self.info("Creating grid")
        self.grid = grid_factory(self.data)

    # ....................... #

    def density(self, specie: str = None) -> np.ndarray:
        key = "Derived_Number_Density"

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def temperature(self, specie: str = None) -> np.ndarray:
        pass

    # ....................... #

    def electric_field(self, component: Union[str, Component] = Component.x):
        pass

    # ....................... #

    def magnetic_field(self, component: Union[str, Component] = Component.x):
        pass

    # ....................... #

    def current(self, component: Union[str, Component] = Component.x):
        pass

    # ....................... #

    def coordinates(self, specie: str):
        key = f"Grid_Particles_{specie}"

        return self._get(key)

    # ....................... #

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
            raise NotImplementedError("Spherical coordinates not implemented")

        elif component is Component.phi:
            if self.grid.dim < 3:
                raise ValueError("Cannot calculate `r` for 1D or 2D grid")

            py = self.momentum(specie, Component.y)
            pz = self.momentum(specie, Component.z)

            return np.arctan2(pz, py)

        elif component is Component.theta:
            raise NotImplementedError("Spherical coordinates not implemented")

        else:
            if component is Component.y and self.grid.dim == 1:
                raise ValueError("Cannot calculate `y` for 1D grid")

            if component is Component.z and self.grid.dim < 3:
                raise ValueError("Cannot calculate `z` for 1D or 2D grid")

            key = f"Particles_P{component.value}_{specie}"

            return self._get(key)
