from typing import List
from pydantic import conint, field_validator, ValidationInfo

from oqd_compiler_infrastructure import VisitableBaseModel

########################################################################################

__all__ = [
    "QuantumBit",
    "ClassicalBit",
    "QuantumRegister",
    "ClassicalRegister",
]

########################################################################################


class QuantumBit(VisitableBaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class ClassicalBit(VisitableBaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class QuantumRegister(VisitableBaseModel):
    id: str = "q"
    reg: List[QuantumBit]

    @field_validator("reg", mode="before")
    @classmethod
    def convert_reg(cls, v, info: ValidationInfo):
        if isinstance(v, int):
            id = info.data.get("id")
            v = [QuantumBit(id=id, index=i) for i in range(v)]
        return v

    # def __getitem__(self, item):
    #     return QuantumRegister(id=self.id, reg=[self.reg[item]])

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            return QuantumRegister(id=self.id, reg=self.reg[start:stop:step])
        else:
            return self.reg[key]


class ClassicalRegister(VisitableBaseModel):
    id: str = "c"
    reg: List[ClassicalBit]

    @field_validator("reg", mode="before")
    @classmethod
    def convert_reg(cls, v, info: ValidationInfo):
        if isinstance(v, int):
            id = info.data.get("id")
            v = [ClassicalBit(id=id, index=i) for i in range(v)]
        return v

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            return ClassicalRegister(id=self.id, reg=self.reg[start:stop:step])
        else:
            return self.reg[key]
