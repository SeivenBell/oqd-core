from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.math import MathExpr
from quantumion.backend.metric import *
from typing import List, Dict, Literal, Tuple
import qutip as qt
from pydantic import ConfigDict
from pydantic.types import NonNegativeInt

__all__ = [
    'QutipOperation',
    'QutipExperiment',
    'TaskArgsQutip',
    'QutipExpectation'
]

class QutipExpectation(VisitableBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    operator: List[Tuple[qt.Qobj, MathExpr]]
    
class TaskArgsQutip(VisitableBaseModel):
    layer: Literal["analog"] = "analog"
    n_shots: Union[int, None] = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Union[EntanglementEntropyReyni, EntanglementEntropyVN, QutipExpectation]] = {}

class QutipOperation(VisitableBaseModel):
    """
    Class representing a quantum operation in qutip

    Attributes:
        hamiltonian (List[qt.Qobj, str]): Hamiltonian to evolve by
        duration (float): Duration of the evolution
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    hamiltonian: List[Tuple[qt.Qobj, MathExpr]]
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
    args: TaskArgsQutip