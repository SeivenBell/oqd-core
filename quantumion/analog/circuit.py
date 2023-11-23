from typing import List, Tuple, Literal, Union
from pydantic import BaseModel, ValidationError
from pydantic.types import NonNegativeInt

from quantumion.analog.gate import AnalogGate
from quantumion.base import TypeReflectBaseModel


class Evolve(TypeReflectBaseModel):
    key: Literal['evolve'] = 'evolve'
    gate: Union[AnalogGate, str]


class Measure(TypeReflectBaseModel):
    key: Literal['measure'] = 'measure'
    qreg: List[NonNegativeInt] = None
    qmode: List[NonNegativeInt] = None


class Initialize(TypeReflectBaseModel):
    key: Literal['initialize'] = 'initialize'


Statement = Union[Initialize, Evolve, Measure]


class AnalogCircuit(TypeReflectBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []

    definitions: List[Tuple[str, AnalogGate]] = []
    sequence: List[Statement] = []

    n_qreg: int = None  # todo: change to a property
    n_qmode: int = None

    class Config:
        extra = "forbid"

    def define(self, id: str, gate: AnalogGate):
        self.definitions.append((id, gate))

    def evolve(self, gate: AnalogGate):
        if not isinstance(gate, AnalogGate):
            raise ValidationError
        if gate.n_qreg != self.n_qreg and self.n_qreg is not None:
            raise ValueError("Inconsistent qreg dimensions.")
        if gate.n_qmode != self.n_qmode and self.n_qmode is not None:
            raise ValueError("Inconsistent qmode dimensions.")

        self.sequence.append(Evolve(gate=gate))
        self.n_qreg = gate.n_qreg
        self.n_qmode = gate.n_qmode

    def measure(self, qreg: List[NonNegativeInt], qmode: List[NonNegativeInt]):
        self.sequence.append(Measure(qreg=qreg, qmode=qmode))


if __name__ == "__main__":
    circuit = AnalogCircuit()