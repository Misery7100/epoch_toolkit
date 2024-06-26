from enum import Enum
from typing import Union

# ----------------------- #


class ExtendedEnum(Enum):
    @classmethod
    def get(cls, v):
        v = getattr(cls, v, None)

        if v is None:
            raise ValueError(f"Invalid value: {v}")

        return v

    # ....................... #

    @classmethod
    def list(cls):
        return list(map(lambda x: x.value, cls))


# ----------------------- #


class Component(ExtendedEnum):
    """Enum class representing different coordinate system components."""

    x = "x"
    y = "y"
    z = "z"
    r = "r"
    r3d = "r3d"
    phi = "phi"
    theta = "theta"


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


class GridData(ExtendedEnum):
    density = "Derived_Number_Density"
    temperature = "Derived_Temperature"
    electric_field = "Electric_Field_E"
    magnetic_field = "Magnetic_Field_B"
    current = "Current_J"
    mass_density = "Derived_Mass_Density"


# ----------------------- #


class ParticleData(ExtendedEnum):
    coordinates = "Grid_Particles"
    momentum = "Particles_P"


# ----------------------- #


class ScalarData(ExtendedEnum):
    total_field_energy = "Total_Field_Energy_in_Simulation__J_"
    total_particle_energy = "Total_Particle_Energy_in_Simulation__J_"
    particle_energy = "Total_Particle_Energy"
    laser_energy_cumsum_inj = "Absorption_Total_Laser_Energy_Injected__J_"
    laser_energy_inv_cumsum_abs = "Absorption_Fraction_of_Laser_Energy_Absorbed____"


# ----------------------- #

EpochData = Union[ParticleData, ScalarData, GridData]

# #! deprecated
# class EpochDataMapping(Enum):
#     density = "Derived_Number_Density"
#     coordinates = "Grid_Particles"
#     momentum = "Particles_P"
#     temperature = "Derived_Temperature"
#     electric_field = "Electric_Field_E"
#     magnetic_field = "Magnetic_Field_B"
#     current = "Current_J"
#     mass_density = "Derived_Mass_Density"


# ----------------------- #
