from quantumion.interface.base import VisitableBaseModel
from quantumion.backend.task import TaskQutip
from quantumion.backend.metric import *
from typing import List, Tuple, Literal
from pydantic import field_validator
import qutip as qt
from pydantic import ConfigDict
from pydantic.types import NonNegativeInt

__all__ = [
    'QutipOperation',
    'QutipExperiment',
]

class QutipOperation(VisitableBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    hamiltonian: List[List]
    duration: float

    @field_validator('hamiltonian')
    @classmethod
    def check_hamiltonian(cls, v):
        for item in v:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError('Each item in the list must be a list with 2 elements')
            if not isinstance(item[0], qt.Qobj) or not isinstance(item[1], str):
                raise ValueError('Incorrect types in hamiltonian')
        return v
    
class QutipExperiment(VisitableBaseModel):
    instructions: list[QutipOperation]
    n_qreg: NonNegativeInt
    n_qmode: NonNegativeInt
    args: TaskQutip