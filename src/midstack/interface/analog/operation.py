from typing import List, Literal, Union
from pydantic.types import NonNegativeInt

from oqd_compiler_infrastructure import VisitableBaseModel

########################################################################################

from .operator import Operator

########################################################################################

__all__ = [
    "AnalogCircuit",
    "AnalogGate",
    "AnalogOperation",
    "Evolve",
    "Measure",
]


########################################################################################


class AnalogOperation(VisitableBaseModel):
    """
    Class representing an analog operation applied to the quantum system
    """

    pass


class AnalogGate(AnalogOperation):
    """
    Class representing an analog gate composed of Hamiltonian terms and dissipation terms

    Attributes:
        hamiltonian (Operator): Hamiltonian terms of the gate
    """

    hamiltonian: Operator


class Evolve(AnalogOperation):
    """
    Class representing an evolution by an analog gate in the analog circuit

    Attributes:
        duration (float): Duration of the evolution
        gate (AnalogGate): Analog gate to evolve by
    """

    key: Literal["evolve"] = "evolve"
    duration: float
    gate: Union[AnalogGate, str]


class Measure(AnalogOperation):
    """
    Class representing a measurement in the analog circuit
    """

    key: Literal["measure"] = "measure"


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

    Attributes:
        sequence (List[Union[Measure, Evolve, Initialize]]): Sequence of statements, including initialize, evolve, measure

    """

    sequence: List[Statement] = []

    n_qreg: Union[NonNegativeInt, None] = None
    n_qmode: Union[NonNegativeInt, None] = None

    def evolve(self, gate: AnalogGate, duration: float):
        self.sequence.append(Evolve(duration=duration, gate=gate))

    def initialize(self):
        self.sequence.append(Initialize())

    def measure(self):
        self.sequence.append(Measure())
