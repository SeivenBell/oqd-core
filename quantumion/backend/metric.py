from typing import List, Union
from quantumion.interface.base import VisitableBaseModel
from pydantic.types import NonNegativeInt
import qutip as qt

########################################################################################

from quantumion.interface.analog.operator import Operator

########################################################################################


class Expectation(VisitableBaseModel):
    operator: Operator

class EntanglementEntropyVN(VisitableBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


class EntanglementEntropyReyni(VisitableBaseModel):
    alpha: NonNegativeInt = 1
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]
