from typing import Union

import numpy as np
from pydantic import BaseModel, model_validator
from sdf import BlockList, BlockPlainMesh

# ----------------------- #


class BaseGrid(BaseModel):
    max_: float
    min_: float
    size: int

    # ....................... #

    @model_validator(mode="before")
    @classmethod
    def check_all(cls, data: dict):
        if data["max_"] <= data["min_"]:
            raise ValueError("max_ should be greater than min_")

        if data["size"] <= 1:
            raise ValueError("size should be greater than 1")

    # ....................... #

    def val_to_idx(self, val: float) -> int:
        return int((val - self.min_) / (self.max_ - self.min_) * self.size)

    # ....................... #

    def idx_to_val(self, idx: int) -> float:
        return idx * (self.max_ - self.min_) / self.size + self.min_


# ----------------------- #


class Grid1D(BaseModel):
    x: BaseGrid

    # ....................... #

    @classmethod
    def from_plain(cls, x_min: float, x_max: float, x_size: int):
        return cls(x=BaseGrid(max_=x_max, min_=x_min, size=x_size))


# ----------------------- #


class Grid2D(BaseModel):
    x: BaseGrid
    y: BaseGrid

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
            x=BaseGrid(max_=x_max, min_=x_min, size=x_size),
            y=BaseGrid(max_=y_max, min_=y_min, size=y_size),
        )


# ----------------------- #


class Grid3D(BaseModel):
    x: BaseGrid
    y: BaseGrid
    z: BaseGrid

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
            x=BaseGrid(max_=x_max, min_=x_min, size=x_size),
            y=BaseGrid(max_=y_max, min_=y_min, size=y_size),
            z=BaseGrid(max_=z_max, min_=z_min, size=z_size),
        )


# ----------------------- #


def grid_factory(
    file: BlockList = None, grid_mid: Union[np.ndarray, BlockPlainMesh] = None
) -> Union[Grid1D, Grid2D, Grid3D]:
    if file is not None:
        grid_mid = file.Grid_Grid_mid.data

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
