from typing import List, Tuple, Literal, Union
from pydantic import ValidationError
from pydantic.types import NonNegativeInt

########################################################################################

from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation

########################################################################################

__all__ = [
    "AnalogCircuit",
    "AnalogGate",
    "AnalogOperation",
    "Evolve",
]


########################################################################################
class AnalogOperation(VisitableBaseModel):
    pass


class AnalogGate(AnalogOperation):
    """
    Class representing an analog gate composed of Hamiltonian terms and dissipation terms

    Args:
        hamiltonian (Operator): Hamiltonian terms of the gate
        dissipation (Dissipation): Dissipative terms of the gate
    """

    hamiltonian: Operator
    dissipation: Dissipation


class Evolve(AnalogOperation):
    """
    Class representing an evolution by an analog gate in the analog circuit

    Args:
        duration (float): Duration of the evolution
        gate (AnalogGate): Analog gate to evolve by
    """

    key: Literal["evolve"] = "evolve"
    duration: float
    gate: Union[AnalogGate, str]


class Measure(AnalogOperation):
    """
    Class representing a measurement in the analog circuit

    Args:
        qreg (list[NonNegativeInt], optional): Indices of the qubit quantum register to measure. Default: None
        qmode (list[NonNegativeInt], optional): Indices of the modal quantum register to measure. Default: None
    """

    key: Literal["measure"] = "measure"
    qreg: Union[List[NonNegativeInt], None] = None
    qmode: Union[List[NonNegativeInt], None] = None


class Initialize(AnalogOperation):
    """
    Class representing a initialization in the analog circuit
    """

    key: Literal["initialize"] = "initialize"


"""
Union of classes 
"""
Statement = Union[Measure, Evolve, Initialize]


class AnalogCircuit(AnalogOperation):
    """
    Class representing a quantum information experiment represented in terms of analog operations.

    Args:
        qreg (list[NonNegativeInt]): Indices of the qubit registers
        qmode (list[NonNegativeInt]): Indices of the bosonic mode registers
        definitions (list[tuple[str, AnalogGate]]): Definitions of gates to unique string identifiers
        sequence (list[Statement]): Sequence of statements, including initialize, evolve, measure

    """

    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []

    definitions: List[Tuple[str, AnalogGate]] = []
    sequence: List[Statement] = []

    n_qreg: Union[NonNegativeInt, None] = None
    n_qmode: Union[NonNegativeInt, None] = None

    class Config:
        extra = "forbid"

    def define(self, id: str, gate: AnalogGate):
        self.definitions.append((id, gate))

    def evolve(self, gate: AnalogGate, duration: float):
        if not isinstance(gate, AnalogGate):
            raise ValidationError
        self.sequence.append(Evolve(duration=duration, gate=gate))

    def measure(self, qreg: List[NonNegativeInt], qmode: List[NonNegativeInt]):
        self.sequence.append(Measure(qreg=qreg, qmode=qmode))
