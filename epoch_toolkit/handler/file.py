import os
from itertools import product
from typing import Any, Dict, Optional, Set, Union

import numpy as np
import sdf_helper as sdfh
from sdf import BlockList

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
    data: BlockList = None
    grid: Grid = None
    structure: Dict[EpochData, Union[Set[str], Dict[str, Set[str]], bool]] = dict()
    species: Set[str] = set()
    unit: Optional[Unit] = None

    header: Dict[str, Any] = dict()
    run_info: Dict[str, Any] = dict()

    # ....................... #

    def __init__(
        self,
        unit: Union[str, Unit] = None,
        verbose: bool = False,
        log_level: str = "info",
        logger_name: str = "File Handler",
    ):
        super().__init__(logger_name=logger_name, log_level=log_level)

        if isinstance(unit, str):
            unit = Unit.get(unit)

        self.unit = unit
        self.verbose = verbose

    # ....................... #

    @property
    def time_fs(self):
        if self.data is not None:
            return self.header["time"] * Unit.femto.value

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

        file_list = sdfh.get_file_list(os.path.dirname(path))

        for f in file_list:
            print(f, sdfh.get_job_id(f))

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

        key = GridData.get("density").value

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def temperature(self, specie: Optional[str] = None) -> np.ndarray:
        assert specie in self.species, f"Invalid specie: {specie}"

        key = GridData.get("temperature").value

        if specie is not None:
            key += f"_{specie}"

        return self._get(key)

    # ....................... #

    def electric_field(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component).value

        key_ = GridData.get("magnetic_field").value
        assert key_ in self.structure.keys(), f"Key not found: {key_}"
        assert component in self.structure[key_], f"Component not found: {component}"

        return self._get(f"{key_}{component}")

    # ....................... #

    def magnetic_field(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component).value

        key_ = GridData.get("magnetic_field").value
        assert key_ in self.structure.keys(), f"Key not found: {key_}"
        assert component in self.structure[key_], f"Component not found: {component}"

        return self._get(f"{key_}{component}")

    # ....................... #

    def current(self, component: Union[str, Component] = Component.get("x")):
        if isinstance(component, str):
            component = Component.get(component).value

        key_ = GridData.get("magnetic_field").value
        assert key_ in self.structure.keys(), f"Key not found: {key_}"
        assert component in self.structure[key_], f"Component not found: {component}"

        return self._get(f"{key_}{component}")

    # ....................... #

    def coordinates(self, specie: str):
        key_ = ParticleData.get("coordinates").value
        assert key_ in self.structure.keys(), f"Key not found: {key_}"
        assert specie in self.structure[key_], f"Specie not found: {specie}"

        return self._get(f"{key_}_{specie}")

    # ....................... #

    # TODO: add support for cylindrical and spherical CS
    # TODO: define abstract transformations for CS
    def momentum(
        self, specie: str, component: Union[str, Component] = Component.get("x")
    ):
        if isinstance(component, str):
            component = Component.get(component)

        if component is Component.r:
            py = self.momentum(specie, Component.y)
            pz = self.momentum(specie, Component.z)

            return np.sqrt(py**2 + pz**2)

        elif component is Component.r3d:
            raise NotImplementedError("Spherical CS not implemented")

        elif component is Component.phi:
            py = self.momentum(specie, Component.y)
            pz = self.momentum(specie, Component.z)

            return np.arctan2(pz, py)

        elif component is Component.theta:
            raise NotImplementedError("Spherical CS not implemented")

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


# ----------------------- #


class FolderHandler(FileHandler):
    def __init__(
        self,
        unit: Union[str, Unit] = None,
        verbose: bool = False,
        log_level: str = "info",
        logger_name: str = "Folder Handler",
    ):
        super().__init__(
            unit=unit,
            verbose=verbose,
            log_level=log_level,
            logger_name=logger_name,
        )

    # ....................... #

    def read(self, folder: str):
        pass
