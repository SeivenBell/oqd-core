from pydantic import BaseModel
from typing import Literal, List, TypedDict, Union

from quantumion.analog.operator import Operator


class Expectation(BaseModel):
    operator: List[Operator]


class EntanglementEntropyVN(BaseModel):
    qreg: List[int] = []
    qmode: List[int] = []


class EntanglementEntropyReyni(BaseModel):
    alpha: int = 1
    qreg: List[int] = []
    qmode: List[int] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]