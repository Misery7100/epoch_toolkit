from typing import List, Optional, Union

from pydantic import BaseModel, model_validator
from sdf import BlockList

from .const import ExtendedEnum, Unit

# ----------------------- #


class Axis(ExtendedEnum):
    x = 0
    y = 1
    z = 2


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

    def val_to_idx(self, val: float, unit: Optional[Unit] = None) -> int:
        if unit is not None:
            val *= unit.value

        return int((val - self.min) / (self.max - self.min) * self.size)

    # ....................... #

    def idx_to_val(self, idx: int, unit: Optional[Unit] = None) -> float:
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

    def component(self, val: Union[str, Axis]) -> BaseGrid:
        if isinstance(val, str):
            val = Axis.get(val)

        assert val.value < self.dim, "Invalid component"

        return self.axes[val.value]

    # ....................... #

    @classmethod
    def from_sdf(cls, file: BlockList) -> "Grid":
        grid_mid = file.Grid_Grid_mid.data
        axes = [BaseGrid(max=g[-1], min=g[0], size=g.size) for g in grid_mid]

        return cls(axes=axes)
