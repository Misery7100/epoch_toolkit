from typing import Union

import numpy as np

# ----------------------- #


def cartesian_to_cylindrical(x: np.ndarray, y: np.ndarray, z: Union[np.ndarray, None]):
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)

    return r, phi, z


# ----------------------- #


def cartesian_to_spherical(x: np.ndarray, y: np.ndarray, z: np.ndarray):
    r = np.sqrt(x**2 + y**2 + z**2)
    phi = np.arctan2(y, x)
    theta = np.arccos(z / r)

    return r, phi, theta


# ----------------------- #


def direction(*args):
    assert len(args) % 2 == 0, "Invalid number of arguments"

    return sum([args[i] * args[i + 1] for i in range(0, len(args), 2)])
