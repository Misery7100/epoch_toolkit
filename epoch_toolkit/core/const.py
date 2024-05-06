from enum import Enum

# ----------------------- #


class Component(Enum):
    x = "x"
    y = "y"
    z = "z"
    r = "r"
    r3d = "r3d"
    phi = "phi"
    theta = "theta"

    # ....................... #

    @classmethod
    def get(cls, v):
        v = getattr(cls, v, None)

        if v is None:
            raise ValueError(f"Invalid component: {v}")

        return v


# ----------------------- #


class Unit(Enum):
    femto = 1e-15
    pico = 1e-12
    nano = 1e-9
    micro = 1e-6
    milli = 1e-3
    centi = 1e-2
    deci = 1e-1
    kilo = 1e3
    mega = 1e6
    giga = 1e9
    tera = 1e12
    peta = 1e15

    # ....................... #

    @classmethod
    def get(cls, v):
        return getattr(cls, v, None)
