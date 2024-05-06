from typing import Literal, Union

import numpy as np
from pydantic import BaseModel, model_validator
from sdf import BlockList, BlockPlainMesh

from .const import Unit

# ----------------------- #


class BaseGrid(BaseModel):
    max: float
    min: float
    size: int
    axis: Literal["x", "y", "z"]

    # ....................... #

    @model_validator(mode="after")
    def check_all(self):
        if self.max <= self.min:
            raise ValueError("max_ should be greater than min_")

        if self.size <= 1:
            raise ValueError("size should be greater than 1")

        return self

    # ....................... #

    def val_to_idx(self, val: float, unit: Unit = None) -> int:
        if unit is not None:
            val *= unit.value

        return int((val - self.min) / (self.max - self.min) * self.size)

    # ....................... #

    def idx_to_val(self, idx: int, unit: Unit = None) -> float:
        multiplier = unit.value if unit is not None else 1

        return (idx * (self.max - self.min) / self.size + self.min) * multiplier


# ----------------------- #


class Grid1D(BaseModel):
    x: BaseGrid
    dim: int = 1

    # ....................... #

    @classmethod
    def from_plain(cls, x_min: float, x_max: float, x_size: int):
        return cls(x=BaseGrid(max=x_max, min=x_min, size=x_size, axis="x"))


# ----------------------- #


class Grid2D(BaseModel):
    x: BaseGrid
    y: BaseGrid
    dim: int = 2

    # ....................... #

    @classmethod
    def from_plain(
        cls,
        x_min: float,
        x_max: float,
        x_size: int,
        y_min: float,
        y_max: float,
        y_size: int,
    ):
        return cls(
            x=BaseGrid(max=x_max, min=x_min, size=x_size, axis="x"),
            y=BaseGrid(max=y_max, min=y_min, size=y_size, axis="y"),
        )


# ----------------------- #


class Grid3D(BaseModel):
    x: BaseGrid
    y: BaseGrid
    z: BaseGrid
    dim: int = 3

    # ....................... #

    @classmethod
    def from_plain(
        cls,
        x_min: float,
        x_max: float,
        x_size: int,
        y_min: float,
        y_max: float,
        y_size: int,
        z_min: float,
        z_max: float,
        z_size: int,
    ):
        return cls(
            x=BaseGrid(max=x_max, min=x_min, size=x_size, axis="x"),
            y=BaseGrid(max=y_max, min=y_min, size=y_size, axis="y"),
            z=BaseGrid(max=z_max, min=z_min, size=z_size, axis="z"),
        )


# ----------------------- #

AbstractGrid = Union[Grid1D, Grid2D, Grid3D]

# ----------------------- #


def grid_factory(
    file: BlockList = None, grid_mid: Union[np.ndarray, BlockPlainMesh] = None
) -> AbstractGrid:

    # whole file
    if file is not None:
        grid_mid = file.Grid_Grid_mid.data

    # grid object
    elif grid_mid is not None:
        if isinstance(grid_mid, BlockPlainMesh):
            grid_mid = grid_mid.data

    if len(grid_mid) == 3:
        xgrid, ygrid, zgrid = grid_mid

        return Grid3D.from_plain(
            x_min=xgrid[0],
            x_max=xgrid[-1],
            x_size=xgrid.size,
            y_min=ygrid[0],
            y_max=ygrid[-1],
            y_size=ygrid.size,
            z_min=zgrid[0],
            z_max=zgrid[-1],
            z_size=zgrid.size,
        )

    elif len(grid_mid) == 2:
        xgrid, ygrid = grid_mid

        return Grid2D.from_plain(
            x_min=xgrid[0],
            x_max=xgrid[-1],
            x_size=xgrid.size,
            y_min=ygrid[0],
            y_max=ygrid[-1],
            y_size=ygrid.size,
        )

    elif len(grid_mid) == 1:
        xgrid = grid_mid

        return Grid1D.from_plain(x_min=xgrid[0], x_max=xgrid[-1], x_size=xgrid.size)

    else:
        raise ValueError("Invalid grid shape")
