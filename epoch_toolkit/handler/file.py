import os  # noqa: F401
from itertools import product
from typing import Any, Callable, Dict, Optional, Set, Union

import numpy as np
import sdf
import sdf_helper as sdfh

from epoch_toolkit.core import (
    Component,
    EpochData,
    Grid,
    GridData,
    ParticleData,
    ScalarData,
    Unit,
)
from epoch_toolkit.utils.logging import LogMixin

# ----------------------- #


class FileHandler(LogMixin):
    data: sdf.BlockList = None
    grid: Grid = None
    structure: Dict[EpochData, Union[Set[str], Dict[str, Set[str]], bool]] = dict()
    species: Set[str] = set()
    _grid_unit: Unit = Unit.nano
    _time_unit: Unit = Unit.femto

    header: Dict[str, Any] = dict()
    run_info: Dict[str, Any] = dict()

    # ....................... #

    def __init__(
        self,
        grid_unit: Optional[Union[str, Unit]] = None,
        time_unit: Optional[Union[str, Unit]] = None,
        verbose: bool = False,
        log_level: str = "info",
        logger_name: str = "File Handler",
    ):
        super().__init__(logger_name=logger_name, log_level=log_level)
        self.set_units(grid_unit=grid_unit, time_unit=time_unit)
        self.verbose = verbose

    # ....................... #

    @property
    def time(self):
        if self.data is not None:
            return self.header["time"] * self._time_unit.value

        else:
            raise ValueError("No data loaded")

    # ....................... #

    def _get(self, key: str):
        if hasattr(self.data, key):
            return getattr(self.data, key).data

        else:
            raise ValueError(f"Key not found: {key}")

    # ....................... #

    def set_units(
        self,
        grid_unit: Optional[Union[str, Unit]] = None,
        time_unit: Optional[Union[str, Unit]] = None,
    ):
        if isinstance(grid_unit, str):
            grid_unit = Unit.get(grid_unit)

        if isinstance(time_unit, str):
            time_unit = Unit.get(time_unit)

        if grid_unit is not None:
            self._grid_unit = grid_unit

        if time_unit is not None:
            self._time_unit = time_unit

    # ....................... #

    def read(self, path: str):
        self.info(f"Reading file: {path}")
        self.data = sdfh.getdata(fname=path, verbose=self.verbose)

        self.info("Capturing grid...")
        self.grid = Grid.from_sdf(self.data)
        self.info(
            "Grid: %sD %s", self.grid.dim, tuple([x.size for x in self.grid.axes])
        )

        self.info("Analyzing data structure...")
        self._analyze()

        self.header = self.data.Header
        self.run_info = self.data.Run_info

    # ....................... #

    def _analyze(self):
        all_keys = set(self.data.__dict__.keys())
        exclude = set()

        for e, k in product(GridData.list(), all_keys.difference(exclude)):
            if k.startswith(e):
                tail = k.split(e)[-1]
                e_name = GridData(e).name

                if tail.startswith("_"):
                    sp = tail[1:]
                    self.species.add(sp)
                    self.structure[e] = self.structure.get(e, set())
                    self.structure[e].add(sp)

                    self.info(f"Add `{e_name}` for specie `{sp}`")

                elif tail:
                    self.structure[e] = self.structure.get(e, set())
                    self.structure[e].add(tail)

                    self.info(f"Add `{e_name}` for component {tail}")

                else:
                    self.structure[e] = self.structure.get(e, set())
                    self.structure[e].add(None)

                    self.info(f"Add `{e_name}` for <NULL> (generailzed)")

                exclude.add(k)

        for e, k in product(ParticleData.list(), all_keys.difference(exclude)):
            if k.startswith(e):
                tail = k.split(e)[-1]
                e_name = ParticleData(e).name

                if tail.startswith("_"):
                    sp = tail[1:]
                    self.species.add(sp)
                    self.structure[e] = self.structure.get(e, set())
                    self.structure[e].add(sp)

                    self.info(f"Add `{e_name}` for specie `{sp}`")

                elif tail:
                    comp, sp = tail.split("_")
                    self.species.add(sp)
                    self.structure[e] = self.structure.get(e, dict())
                    self.structure[e][comp] = self.structure[e].get(comp, set())
                    self.structure[e][comp].add(sp)

                    self.info(f"Add `{e_name}` `{comp}` component for specie `{sp}`")

                exclude.add(k)

        for e, k in product(ScalarData.list(), all_keys.difference(exclude)):
            if k == e:
                e_name = ScalarData(e).name

                self.structure[k] = True
                self.info(f"Add `{e_name}`")

    # ....................... #

    def density(self, specie: Optional[str] = None) -> np.ndarray:
        assert specie in self.species, f"Invalid specie: {specie}"
        assert GridData.get("density").value in self.structure.keys()

        key = GridData.get("density").value
        assert key in self.structure.keys(), f"Key not found: {key}"

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def temperature(self, specie: Optional[str] = None) -> np.ndarray:
        assert specie in self.species, f"Invalid specie: {specie}"

        key = GridData.get("temperature").value
        assert key in self.structure.keys(), f"Key not found: {key}"

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def electric_field(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component)

        if component not in [Component.x, Component.y, Component.z]:
            return self._non_cartesian_grid(self.current, component, self.grid)

        else:
            component = component.value
            key_ = GridData.get("magnetic_field").value
            assert key_ in self.structure.keys(), f"Key not found: {key_}"
            assert (
                component in self.structure[key_]
            ), f"Component not found: {component}"

            return self._get(f"{key_}{component}")

    # ....................... #

    def magnetic_field(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component)

        if component not in [Component.x, Component.y, Component.z]:
            return self._non_cartesian_grid(self.current, component, self.grid)

        else:
            component = component.value
            key_ = GridData.get("magnetic_field").value
            assert key_ in self.structure.keys(), f"Key not found: {key_}"
            assert (
                component in self.structure[key_]
            ), f"Component not found: {component}"

            return self._get(f"{key_}{component}")

    # ....................... #

    def current(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component)

        if component not in [Component.x, Component.y, Component.z]:
            return self._non_cartesian_grid(self.current, component, self.grid)

        else:
            component = component.value
            key_ = GridData.get("magnetic_field").value
            assert key_ in self.structure.keys(), f"Key not found: {key_}"
            assert (
                component in self.structure[key_]
            ), f"Component not found: {component}"

            return self._get(f"{key_}{component}")

    # ....................... #

    def coordinates(self, specie: str):
        key_ = ParticleData.get("coordinates").value
        assert key_ in self.structure.keys(), f"Key not found: {key_}"
        assert specie in self.structure[key_], f"Specie not found: {specie}"

        return self._get(f"{key_}_{specie}")

    # ....................... #

    @staticmethod
    def _non_cartesian_grid(
        func: Callable, component: Union[str, Component], grid: Grid
    ):
        if isinstance(component, str):
            component = Component.get(component)

        assert component in [Component.r, Component.r3d, Component.phi, Component.theta]

        if component is Component.r:
            yv = func(component=Component.y)
            zv = func(component=Component.z)

            ygrid = grid.component("y")
            zgrid = grid.component("z")

            ygrid = np.linspace(ygrid.min, ygrid.max, ygrid.size, endpoint=True)
            zgrid = np.linspace(zgrid.min, zgrid.max, zgrid.size, endpoint=True)

            ygrid, zgrid = np.meshgrid(ygrid, zgrid, indexing="ij")

            dot = yv * ygrid + zv * zgrid

            return np.sqrt(yv**2 + zv**2) * np.sign(dot)

        elif component is Component.r3d:
            xv = func(component=Component.x)
            yv = func(component=Component.y)
            zv = func(component=Component.z)

            xgrid = grid.component("x")
            ygrid = grid.component("y")
            zgrid = grid.component("z")

            xgrid = np.linspace(xgrid.min, xgrid.max, xgrid.size, endpoint=True)
            ygrid = np.linspace(ygrid.min, ygrid.max, ygrid.size, endpoint=True)
            zgrid = np.linspace(zgrid.min, zgrid.max, zgrid.size, endpoint=True)

            xgrid, ygrid, zgrid = np.meshgrid(xgrid, ygrid, zgrid, indexing="ij")

            dot = xv * xgrid + yv * ygrid + zv * zgrid

            return np.sqrt(xv**2 + yv**2 + zv**2) * np.sign(dot)

        elif component is Component.phi:
            yv = func(component=Component.y)
            zv = func(component=Component.z)

            return np.arctan2(zv, yv)

        else:
            xv = func(component=Component.x)
            yv = func(component=Component.y)
            zv = func(component=Component.z)

            return np.arccos(zv / np.sqrt(xv**2 + yv**2 + zv**2))

    # ....................... #

    @staticmethod
    def _non_cartesian_particle(
        func: Callable,
        coordinate_func: Callable,
        component: Union[str, Component],
        specie: Optional[str] = None,
    ):

        if isinstance(component, str):
            component = Component.get(component)

        assert component in [Component.r, Component.r3d, Component.phi, Component.theta]

        if component is Component.r:
            yv = func(component=Component.y, specie=specie)
            zv = func(component=Component.z, specie=specie)

            xyz = coordinate_func(specie)
            dot = yv * xyz[1] + zv * xyz[2]

            return np.sqrt(yv**2 + zv**2) * np.sign(dot)

        elif component is Component.r3d:
            xv = func(component=Component.x, specie=specie)
            yv = func(component=Component.y, specie=specie)
            zv = func(component=Component.z, specie=specie)

            xyz = coordinate_func(specie)
            dot = xv * xyz[0] + yv * xyz[1] + zv * xyz[2]

            return np.sqrt(xv**2 + yv**2 + zv**2) * np.sign(dot)

        elif component is Component.phi:
            yv = func(component=Component.y, specie=specie)
            zv = func(component=Component.z, specie=specie)

            return np.arctan2(zv, yv)

        else:
            xv = func(component=Component.x, specie=specie)
            yv = func(component=Component.y, specie=specie)
            zv = func(component=Component.z, specie=specie)

            return np.arccos(zv / np.sqrt(xv**2 + yv**2 + zv**2))

    # ....................... #

    def momentum(
        self,
        specie: str,
        component: Union[str, Component] = Component.get("x"),
    ):
        if isinstance(component, str):
            component = Component.get(component)

        if component not in [Component.x, Component.y, Component.z]:
            return self._non_cartesian_particle(
                self.momentum, self.coordinates, component, specie=specie
            )

        else:
            component = component.value
            key_ = ParticleData.get("momentum").value

            assert key_ in self.structure.keys(), f"Key not found: {key_}"
            assert (
                component in self.structure[key_].keys()
            ), f"Component not found: {component}"
            assert (
                specie in self.structure[key_][component]
            ), f"Specie not found: {specie}"

            return self._get(f"{key_}{component}_{specie}")
