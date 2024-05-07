from enum import Enum

# ----------------------- #


class Component(Enum):
    """Enum class representing different coordinate system components."""

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
    """Enumeration class representing different units of measurement."""

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


# ----------------------- #


class EpochDataMapping(Enum):
    density = "Derived_Number_Density"
    coordinates = "Grid_Particles"
    momentum = "Particles_P"
    temperature = "Derived_Temperature"
    electric_field = "Electric_Field_E"
    magnetic_field = "Magnetic_Field_B"
    current = "Current_J"
