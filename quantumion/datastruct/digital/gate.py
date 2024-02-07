from typing import List, Union, Optional

########################################################################################

from quantumion.datastruct.base import VisitableBaseModel
from quantumion.datastruct.digital.register import (
    QuantumRegister,
    ClassicalRegister,
    QuantumBit,
    ClassicalBit,
)

########################################################################################

__all__ = ["GateParameters", "Gate"]

########################################################################################


class GateParameters(VisitableBaseModel):
    vals: List[Union[int, float]] = []


class Gate(VisitableBaseModel):
    name: str
    qreg: Optional[Union[QuantumRegister, QuantumBit]] = None
    creg: Optional[Union[ClassicalRegister, ClassicalBit]] = None
    params: Optional[GateParameters] = None

    @property
    def qasm(self):
        _str = f"{self.name} "
        if isinstance(self.qreg, QuantumBit):
            _str += f"{self.qreg.id}[{self.qreg.index}]"
        elif isinstance(self.qreg, QuantumRegister):
            _str += f",".join([f"{reg.id}[{reg.index}]" for reg in self.qreg.reg])
        _str += ";\n"
        return _str


def H(**kwargs):
    return Gate(name="h", **kwargs)


def CNOT(**kwargs):
    return Gate(name="cx", **kwargs)
