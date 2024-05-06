from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel, model_validator

from ..const import Unit
from ..grid import AbstractGrid, BaseGrid

# ----------------------- #


class GridCrop(BaseModel):
    min: float
    max: float
    grid: BaseGrid
    unit: Optional[Unit] = None

    # ....................... #

    @model_validator(mode="after")
    def check_all(self):
        if self.max <= self.min:
            raise ValueError("max should be greater than min")

        return self

    # ....................... #

    def apply(self, arr: np.ndarray) -> np.ndarray:
        min_idx = self.grid.val_to_idx(self.min, unit=self.unit)
        max_idx = self.grid.val_to_idx(self.max, unit=self.unit)

        ndims = arr.ndim
        slices = [slice(None)] * ndims

        if self.grid.axis == "x":
            slices[0] = slice(min_idx, max_idx)

        elif self.grid.axis == "y" and ndims > 1:
            slices[1] = slice(min_idx, max_idx)

        elif self.grid.axis == "z" and ndims > 2:
            slices[2] = slice(min_idx, max_idx)

        else:
            raise ValueError(f"Invalid axis: {self.grid.axis}")

        return arr[tuple(slices)]

    # ....................... #

    @classmethod
    def from_abstract_grid(
        cls,
        min: float,
        max: float,
        axis: Literal["x", "y", "z"],
        grid: AbstractGrid,
        unit: Unit = None,
    ) -> "GridCrop":
        try:
            target_grid = getattr(grid, axis)

        except AttributeError:
            raise ValueError(f"Axis `{axis}` not found in grid")

        return cls(min=min, max=max, grid=target_grid, unit=unit)
