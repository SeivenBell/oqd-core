from typing import List, Union
from quantumion.interface.base import VisitableBaseModel
from pydantic.types import NonNegativeInt

########################################################################################

from quantumion.interface.analog.operator import Operator

########################################################################################


class Expectation(VisitableBaseModel):
    operator: Operator

class QutipExpectation(VisitableBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    operator: List[List]

    @field_validator('operator')
    @classmethod
    def check_operator(cls, v):
        for item in v:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError('Each item in the list must be a list with 2 elements')
            if not isinstance(item[0], qt.Qobj) or not isinstance(item[1], str):
                raise ValueError('Incorrect types in operator')
        return v

class EntanglementEntropyVN(VisitableBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


class EntanglementEntropyReyni(VisitableBaseModel):
    alpha: NonNegativeInt = 1
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]
