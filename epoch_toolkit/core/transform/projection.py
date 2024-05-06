from typing import Literal

import numpy as np
from pydantic import BaseModel

# ----------------------- #


class PlaneProjection(BaseModel):
    axis: Literal["x", "y", "z"]

    # ....................... #

    def apply(self, arr: np.ndarray) -> np.ndarray:
        if self.axis == "x":
            return arr.sum(axis=0)

        elif self.axis == "y":
            if arr.ndim <= 1:
                raise ValueError("Cannot project along y-axis for 1D array")

            return arr.sum(axis=1)

        else:
            if arr.ndim <= 2:
                raise ValueError("Cannot project along z-axis for 1D or 2D array")

            return arr.sum(axis=2)
