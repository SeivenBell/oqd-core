from typing import List
from pydantic import BaseModel, ValidationError

from quantumion.analog.gate import AnalogGate


class Statement(BaseModel):
    key: str
    assignment: AnalogGate


class AnalogCircuit(BaseModel):
    definitions: List[int] = []
    registers: List[int] = []
    sequence: List[AnalogGate] = []

    n_qreg: int = None  # todo: change to a property
    n_qmode: int = None

    class Config:
        extra = "forbid"

    def add(self, gate: AnalogGate):
        if not isinstance(gate, AnalogGate):
            raise ValidationError
        if gate.n_qreg != self.n_qreg and self.n_qreg is not None:
            raise ValueError("Inconsistent qreg dimensions.")
        if gate.n_qmode != self.n_qmode and self.n_qmode is not None:
            raise ValueError("Inconsistent qmode dimensions.")

        self.sequence.append(gate)
        self.n_qreg = gate.n_qreg
        self.n_qmode = gate.n_qmode
