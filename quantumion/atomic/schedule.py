# External imports

from pydantic import BaseModel
from typing import Union

########################################################################################

from typing import List, Tuple, Dict, Optional, Callable, Union, Literal
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    PositiveInt,
    NonNegativeInt,
    validator,
    AfterValidator,
    NonNegativeFloat,
    model_validator,
    field_validator,
    ValidationError,
)

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


class Level(BaseModel):
    principal: NonNegativeInt
    spin: NonNegativeAngularMomentumNumber
    orbital: NonNegativeAngularMomentumNumber
    nuclear: NonNegativeAngularMomentumNumber
    spin_orbital: NonNegativeAngularMomentumNumber
    spin_orbital_nuclear: NonNegativeAngularMomentumNumber
    spin_orbital_nuclear_magnetization: AngularMomentumNumber
    energy: float

    @model_validator(mode="after")
    def orbital_validate(self):
        if self.orbital >= self.principal:
            raise ValueError("Invalid orbital quantum # (L)")
        return self

    @model_validator(mode="after")
    def spin_orbital_validate(self):
        if (
            self.spin_orbital < abs(self.spin - self.orbital)
            or self.spin_orbital > self.spin + self.orbital
        ):
            raise ValueError("Invalid spin orbital quantum # (J)")
        return self

    @model_validator(mode="after")
    def spin_orbital_nuclear_validate(self):
        if (
            self.spin_orbital_nuclear < abs(self.spin_orbital - self.nuclear)
            or self.spin_orbital_nuclear > self.spin_orbital + self.nuclear
        ):
            raise ValueError("Invalid spin orbital nuclear quantum # (F)")
        return self

    @model_validator(mode="after")
    def spin_orbital_nuclear_magnetization_validate(self):
        if abs(self.spin_orbital_nuclear_magnetization) > self.spin_orbital_nuclear:
            raise ValueError("Invalid spin orbital nuclear magnetization (m_F)")
        elif not (
            self.spin_orbital_nuclear_magnetization - self.spin_orbital_nuclear
        ).is_integer():
            raise ValueError("Invalid spin orbital nuclear magnetization (m_F)")
        return self


class Multipole(BaseModel):
    field: Literal["E", "M"]
    pole: PositiveInt


class Transition(BaseModel):
    level1: Level
    level2: Level
    multipole: Multipole
    einstein_A: float
    pass


class Ion(BaseModel):
    mass: float
    charge: float
    levels: List[Level]
    transitions: List[Transition]
    pass


########################################################################################


class Pulse(BaseModel):
    ion: Ion
    transition: Transition
    rabi: Union[float, Callable[[float], float]]
    detuning: Union[float, Callable[[float], float]]
    polarization: Union[List[float], Callable[[float], List[float]]]
    wavevector: Union[List[float], Callable[[float], List[float]]]


class Protocol(BaseModel):
    pulses: List[Pulse]


########################################################################################


class Apply(BaseModel):
    protocol: Protocol
    time: float


########################################################################################


class Schedule(BaseModel):
    statements: List[Apply]


########################################################################################

if __name__ == "__main__":

    try:
        level1 = Level(
            principal=6,
            spin=0.5,
            orbital=0,
            nuclear=0.5,
            spin_orbital=0.5,
            spin_orbital_nuclear=0,
            spin_orbital_nuclear_magnetization=0,
            energy=0,
        )
    except ValidationError as e:
        print(e)
