from typing import List, Tuple, Literal, Union
from pydantic import ValidationError
from pydantic.types import NonNegativeInt

########################################################################################

from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.analog.gate import AnalogGate

########################################################################################

__all__ = [
    "Evolve",
    "Measure",
    "Initialize",
    "AnalogCircuit",
]

########################################################################################


class Evolve(VisitableBaseModel):
    key: Literal["evolve"] = "evolve"
    gate: Union[AnalogGate, str]


class Measure(VisitableBaseModel):
    key: Literal["measure"] = "measure"
    qreg: Union[List[NonNegativeInt], None] = None
    qmode: Union[List[NonNegativeInt], None] = None


class Initialize(VisitableBaseModel):
    key: Literal["initialize"] = "initialize"


Statement = Union[Measure, Evolve, Initialize]


class AnalogCircuit(VisitableBaseModel):
    """

    Examples:
        >>> AnalogCircuit().evolve(AnalogGate(duration=1.0, hamiltonian=[PauliX]))

    Args:
        qreg (list[NonNegativeInt]): indices of the qubit registers
        qmode (list[NonNegativeInt]): indices of the bosonic mode registers
        definitions (list[tuple[str, AnalogGate]]): definitions of gates to unique string identifiers
        sequence (list[Statement]): sequence of statements, including initialize, evolve, measure

    """

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
