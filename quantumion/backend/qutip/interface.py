from quantumion.interface.base import VisitableBaseModel
from quantumion.backend.task import TaskArgsAnalog
from quantumion.backend.metric import *
from typing import List, Tuple, Literal
import qutip as qt
from pydantic import ConfigDict
from pydantic.types import NonNegativeInt

__all__ = [
    "QutipOperation",
    "QutipExperiment",
]


class QutipOperation(VisitableBaseModel):
    """
    Class representing a quantum operation in qutip

    Attributes:
        hamiltonian (List[qt.Qobj, str]): Hamiltonian to evolve by
        duration (float): Duration of the evolution
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    hamiltonian: list[Tuple[qt.Qobj, str]]
    duration: float


class QutipExperiment(VisitableBaseModel):
    """
    Class representing a quantum experiment in qutip

    Attributes:
        instructions (List[QutipOperation]): List of quantum operations to apply
        n_qreg (NonNegativeInt): Number of qubit quantum registers
        n_qmode (NonNegativeInt): Number of modal quantum registers
        args (TaskArgsAnalog): Arguments for the experiment
    """

    instructions: list[QutipOperation]
    n_qreg: NonNegativeInt
    n_qmode: NonNegativeInt
    args: TaskArgsAnalog
