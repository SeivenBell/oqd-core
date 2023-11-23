from typing import Literal, List, TypedDict, Union
from pydantic.types import NonNegativeInt

from backends.base import TypeReflectBaseModel
from quantumion.analog.operator import Operator


class Expectation(TypeReflectBaseModel):
    operator: List[Operator]


class EntanglementEntropyVN(TypeReflectBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


class EntanglementEntropyReyni(TypeReflectBaseModel):
    alpha: NonNegativeInt = 1
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]
