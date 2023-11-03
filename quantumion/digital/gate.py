# External imports

from typing import List, Union, Optional, Literal

from pydantic import BaseModel


########################################################################################

# Internal exports

from quantumion.digital.register import (
    QuantumRegister,
    ClassicalRegister,
    QuantumBit,
    ClassicalBit,
)

########################################################################################


class GateParameters(BaseModel):
    vals: List[Union[int, float]] = []


class Gate(BaseModel):
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


class H(Gate):
    name: Literal["h"] = "h"


class CNOT(Gate):
    name: Literal["h"] = "cx"
