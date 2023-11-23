from typing import Literal, Union
from pydantic import BaseModel

from quantumion.digital.register import QuantumRegister, ClassicalRegister


class Statement(BaseModel):
    statement: str


class Barrier(Statement):
    statement: Literal["barrier"] = "barrier"
    reg: Union[QuantumRegister, ClassicalRegister]


class Measure(Statement):
    statement: Literal["measure"] = "measure"
    qreg: QuantumRegister = None

    @property
    def qasm(self):
        return f"{self.statement};\n"
