from typing import List, Tuple, Literal, Union, Optional
from pydantic import BaseModel, ValidationError
from pydantic.types import NonNegativeInt

from quantumion.analog.gate import AnalogGate


class Evolve(BaseModel):
    key: Literal['evolve'] = 'evolve'
    gate: Union[AnalogGate, str]


class Measure(BaseModel):
    key: Literal['measure'] = 'measure'
    qreg: Union[List[NonNegativeInt], None] = None
    qmode: Union[List[NonNegativeInt], None] = None


class Initialize(BaseModel):
    key: Literal['initialize'] = 'initialize'


Statement = Union[Measure, Evolve, Initialize]


class AnalogCircuit(BaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []

    definitions: List[Tuple[str, AnalogGate]] = []
    sequence: List[Statement] = []

    n_qreg: int = 0  # todo: change to a property
    n_qmode: int = 0

    class Config:
        extra = "forbid"

    def define(self, id: str, gate: AnalogGate):
        self.definitions.append((id, gate))

    def evolve(self, gate: AnalogGate):
        if not isinstance(gate, AnalogGate):
            raise ValidationError
        if self.n_qreg != 0 and gate.n_qreg != self.n_qreg:
            raise ValueError("Inconsistent qreg dimensions.")
        if self.n_qmode != 0 and gate.n_qmode != self.n_qmode:
            raise ValueError("Inconsistent qmode dimensions.")

        self.sequence.append(Evolve(gate=gate))
        self.n_qreg = gate.n_qreg
        self.n_qmode = gate.n_qmode

    def measure(self, qreg: List[NonNegativeInt], qmode: List[NonNegativeInt]):
        self.sequence.append(Measure(qreg=qreg, qmode=qmode))


if __name__ == "__main__":
    circuit = AnalogCircuit()