from enum import Enum
from typing import List, Union

from pydantic import BaseModel, model_validator
from sdf import BlockList

from .const import Unit

# ----------------------- #


class GridAxis(Enum):
    x = 0
    y = 1
    z = 2

    # ....................... #

    @classmethod
    def get(cls, v):
        v = getattr(cls, v, None)

        if v is None:
            raise ValueError(f"Invalid component: {v}")

        return v


# ----------------------- #


class BaseGrid(BaseModel):
    max: float
    min: float
    size: int

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


class Grid(BaseModel):
    axes: List[BaseGrid]

    # ....................... #

    @property
    def dim(self):
        return len(self.axes)

    # ....................... #

    def component(self, val: Union[str, GridAxis]) -> BaseGrid:
        if isinstance(val, str):
            val = GridAxis.get(val)

        return self.axes[val.value]

    # ....................... #

    @classmethod
    def from_sdf(cls, file: BlockList) -> "Grid":
        grid_mid = file.Grid_Grid_mid.data

        config = []

        for g in grid_mid:
            min_ = g[0]
            max_ = g[-1]
            size = g.size

            config.append((min_, max_, size))

        axes = [BaseGrid(max=max_, min=min_, size=size) for min_, max_, size in config]

        return cls(axes=axes)
