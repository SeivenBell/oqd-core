# External imports
from typing import List, Tuple, Dict, Optional, Callable, Union, Literal
from typing_extensions import Annotated
from pydantic import (
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

from quantumion.base import TypeReflectBaseModel

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


class Multipole(TypeReflectBaseModel):
    field: Literal["E", "M"]
    pole: PositiveInt


class Transition(TypeReflectBaseModel):
    level1: Level
    level2: Level
    multipole: Multipole
    einstein_A: float
    pass


class Ion(TypeReflectBaseModel):
    mass: float
    charge: float
    levels: List[Level]
    transitions: List[Transition]
    pass


########################################################################################


class Pulse(TypeReflectBaseModel):
    ion: Ion
    transition: Transition
    rabi: Union[float, Callable[[float], float]]
    detuning: Union[float, Callable[[float], float]]
    polarization: Union[List[float], Callable[[float], List[float]]]
    wavevector: Union[List[float], Callable[[float], List[float]]]


class Protocol(TypeReflectBaseModel):
    pulses: List[Pulse]


########################################################################################


class Apply(TypeReflectBaseModel):
    protocol: Protocol
    time: float


########################################################################################


class AtomicProgram(TypeReflectBaseModel):
    statements: List[Apply]


########################################################################################

if __name__ == "__main__":
    try:
        import numpy as np

        dark_state = Level(
            principal=6,
            spin=0.5,
            orbital=0,
            nuclear=0.5,
            spin_orbital=0.5,
            spin_orbital_nuclear=0,
            spin_orbital_nuclear_magnetization=0,
            energy=0,
        )
        bright_state = Level(
            principal=6,
            spin=0.5,
            orbital=0,
            nuclear=0.5,
            spin_orbital=0.5,
            spin_orbital_nuclear=1,
            spin_orbital_nuclear_magnetization=0,
            energy=12.6428e9,
        )
        excited_state = Level(
            principal=6,
            spin=0.5,
            orbital=1,
            nuclear=0.5,
            spin_orbital=0.5,
            spin_orbital_nuclear=0,
            spin_orbital_nuclear_magnetization=0,
            energy=811.29e12,
        )
        excited_state_2 = Level(
            principal=6,
            spin=0.5,
            orbital=1,
            nuclear=0.5,
            spin_orbital=0.5,
            spin_orbital_nuclear=1,
            spin_orbital_nuclear_magnetization=0,
            energy=811.29e12 + 2.105e9,
        )
        transition_1 = Transition(
            level1=dark_state,
            level2=excited_state_2,
            multipole=Multipole(field="E", pole=1),
            einstein_A=1,
        )
        transition_2 = Transition(
            level1=bright_state,
            level2=excited_state,
            multipole=Multipole(field="E", pole=1),
            einstein_A=1,
        )

        yb171plus = Ion(
            mass=171,
            charge=1,
            levels=[dark_state, bright_state, excited_state, excited_state_2],
            transitions=[transition_1, transition_2],
        )

        raman1 = Pulse(
            ion=yb171plus,
            transition=yb171plus.transitions[0],
            rabi=1e6 * 2 * np.pi,
            detuning=1e9,
            polarization=[1, 0, 0],
            wavevector=[0, 0, 1],
        )
        raman2 = Pulse(
            ion=yb171plus,
            transition=yb171plus.transitions[1],
            rabi=1e6 * 2 * np.pi,
            detuning=1e9,
            polarization=[0, 0, 1],
            wavevector=[0, 0, 1],
        )

        twophotonraman = Protocol(pulses=[raman1, raman2])

        program = AtomicProgram(
            statements=[Apply(protocol=twophotonraman, time=0.5e-6)]
        )

    except ValidationError as e:
        print(e)
