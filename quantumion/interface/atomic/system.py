# External imports
from typing import List, Literal, Optional
from typing_extensions import Annotated
from pydantic import (
    PositiveInt,
    NonNegativeInt,
    AfterValidator,
    NonNegativeFloat,
    model_validator,
)

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel

########################################################################################

__all__ = [
    "Level",
    "Transition",
    "Ion",
    "Mode",
    "System",
]

########################################################################################


def is_halfint(v: float) -> float:
    if not (v * 2).is_integer():
        raise ValueError()
    return v


########################################################################################


AngularMomentumNumber = Annotated[float, AfterValidator(is_halfint)]
NonNegativeAngularMomentumNumber = Annotated[
    NonNegativeFloat, AfterValidator(is_halfint)
]

# ########################################################################################


class Level(TypeReflectBaseModel):
    principal: Optional[NonNegativeInt] = None
    spin: Optional[NonNegativeAngularMomentumNumber] = None
    orbital: Optional[NonNegativeAngularMomentumNumber] = None
    nuclear: Optional[NonNegativeAngularMomentumNumber] = None
    spin_orbital: Optional[NonNegativeAngularMomentumNumber] = None
    spin_orbital_nuclear: Optional[NonNegativeAngularMomentumNumber] = None
    spin_orbital_nuclear_magnetization: Optional[AngularMomentumNumber] = None
    energy: float

    # @model_validator(mode="after")
    # def orbital_validate(self):
    #     if self.orbital >= self.principal:
    #         raise ValueError("Invalid orbital quantum # (L)")
    #     return self

    # @model_validator(mode="after")
    # def spin_orbital_validate(self):
    #     if (
    #         self.spin_orbital < abs(self.spin - self.orbital)
    #         or self.spin_orbital > self.spin + self.orbital
    #     ):
    #         raise ValueError("Invalid spin orbital quantum # (J)")
    #     return self

    # @model_validator(mode="after")
    # def spin_orbital_nuclear_validate(self):
    #     if (
    #         self.spin_orbital_nuclear < abs(self.spin_orbital - self.nuclear)
    #         or self.spin_orbital_nuclear > self.spin_orbital + self.nuclear
    #     ):
    #         raise ValueError("Invalid spin orbital nuclear quantum # (F)")
    #     return self

    # @model_validator(mode="after")
    # def spin_orbital_nuclear_magnetization_validate(self):
    #     if abs(self.spin_orbital_nuclear_magnetization) > self.spin_orbital_nuclear:
    #         raise ValueError("Invalid spin orbital nuclear magnetization (m_F)")
    #     elif not (
    #         self.spin_orbital_nuclear_magnetization - self.spin_orbital_nuclear
    #     ).is_integer():
    #         raise ValueError("Invalid spin orbital nuclear magnetization (m_F)")
    #     return self


class Transition(TypeReflectBaseModel):
    level1: Level
    level2: Level
    einsteinA: float
    pass


class Ion(TypeReflectBaseModel):
    mass: float
    charge: float
    levels: List[Level]
    transitions: List[Transition]
    pass


########################################################################################


class Mode(TypeReflectBaseModel):
    energy: float


########################################################################################


class System(TypeReflectBaseModel):
    ions: List[Ion]
    modes: List[Mode]
