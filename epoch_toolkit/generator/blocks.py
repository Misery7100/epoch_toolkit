# TODO: write definitions for EPOCH blocks
# TODO: a proper serialization for input files with <-> transformation

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

# ----------------------- #


class NumberWithUnits(BaseModel):
    """Number with units"""

    value: float
    unit: Optional[str] = "nano"  # TODO: use enum for units ?


# ----------------------- #


class EpochBoundaryConditions(Enum):
    simple_laser = "simple_laser"
    simple_outflow = "simple_outflow"
    conduct = "conduct"
    cpml_laser = "cpml_laser"
    cpml_outflow = "cpml_outflow"


# ----------------------- #


class Control(BaseModel):
    """Control block for EPOCH"""

    # grid parameters
    nx: int
    ny: Optional[int] = None
    nz: Optional[int] = None

    x_max: NumberWithUnits
    x_min: NumberWithUnits
    y_max: Optional[NumberWithUnits] = None
    y_min: Optional[NumberWithUnits] = None
    z_max: Optional[NumberWithUnits] = None
    z_min: Optional[NumberWithUnits] = None

    # modeling time
    t_end: NumberWithUnits

    # optimization flags
    simplify_deck: bool = True
    use_current_correction: bool = True

    # optional parameters
    particle_tstart: Optional[NumberWithUnits] = NumberWithUnits(
        value=0.0, unit="femto"
    )

    # output parameters
    stdout_frequency: int = 20


# ----------------------- #


class Constant(BaseModel):
    pass  # ? And how to define fully custom stuff? :D


# ----------------------- #


class Boundaries(BaseModel):
    """Boundary conditions for EPOCH"""

    bc_x_min: EpochBoundaryConditions
    bc_x_max: EpochBoundaryConditions
    bc_y_min: Optional[EpochBoundaryConditions] = None
    bc_y_max: Optional[EpochBoundaryConditions] = None
    bc_z_min: Optional[EpochBoundaryConditions] = None
    bc_z_max: Optional[EpochBoundaryConditions] = None


# ----------------------- #


class Subset(BaseModel):
    name: str
    gamma_min: Optional[int] = None
    gamma_max: Optional[int] = None
    include_species: List[str]


# ----------------------- #


class OutputGridItem(BaseModel):
    name: str
    constraints: List[str] = ["always"]


# ----------------------- #


class OutputParticleItem(BaseModel):
    name: str
    constraints: List[str] = ["always"]


# ----------------------- #


class OutputMetricItem(BaseModel):  # TODO: check with EPOCH docs to rename
    name: str
    constraints: List[str] = ["always"]


# ----------------------- #


class Output(BaseModel):
    dt_snapshot: NumberWithUnits
    name: str
    file_prefix: Optional[str] = None
    items: List[Union[OutputGridItem, OutputParticleItem, OutputMetricItem]]


# ----------------------- #


class Species(BaseModel):
    name: str
    charge: int
    mass: float

    temp_ev: float
    npart_per_cell: int = 50
    density: str  # TODO: replace with some specific definition ?


# ----------------------- #


class Laser(BaseModel):
    boundary: str  # TODO: replace with enum definition
    intensity_w_cm2: float
    wavelength: NumberWithUnits
    profile: str  # TODO: replace with some specific definition ?
    t_profile: str  # TODO: replace with some specific definition ?
    t_end: NumberWithUnits
    pol: str  # TODO: replace with some specific definition ?
    phase: str  # TODO: replace with some specific definition ?
