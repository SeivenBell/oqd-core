from typing import List, Union

from pydantic.types import NonNegativeInt

from oqd_compiler_infrastructure import VisitableBaseModel

########################################################################################

from ..interface.analog.operator import Operator, OperatorSubtypes

########################################################################################

__all__ = [
    "Expectation",
    "EntanglementEntropyReyni",
    "EntanglementEntropyVN",
]

########################################################################################


class Expectation(VisitableBaseModel):
    operator: OperatorSubtypes


class EntanglementEntropyVN(VisitableBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


class EntanglementEntropyReyni(VisitableBaseModel):
    alpha: NonNegativeInt = 1
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]
