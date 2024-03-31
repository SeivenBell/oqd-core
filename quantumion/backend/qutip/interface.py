from quantumion.interface.base import VisitableBaseModel
from quantumion.backend.task import TaskArgsAnalog
from quantumion.backend.metric import *
from typing import List, Tuple, Literal
import qutip as qt
from pydantic import ConfigDict
from pydantic.types import NonNegativeInt

__all__ = [
    'QutipOperation',
    'QutipExperiment',
]

class QutipOperation(VisitableBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    hamiltonian: list[Tuple[qt.Qobj, str]]
    duration: float
    
class QutipExperiment(VisitableBaseModel):
    instructions: list[QutipOperation]
    n_qreg: NonNegativeInt
    n_qmode: NonNegativeInt
    args: TaskArgsAnalog