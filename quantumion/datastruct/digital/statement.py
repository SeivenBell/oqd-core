from typing import Literal, Union

########################################################################################


from quantumion.datastruct.base import VisitableBaseModel
from quantumion.datastruct.digital.register import QuantumRegister, ClassicalRegister

########################################################################################

__all__ = [
    "Statement",
    "Barrier",
]

########################################################################################


class Barrier(VisitableBaseModel):
    statement: Literal["barrier"] = "barrier"
    reg: Union[QuantumRegister, ClassicalRegister]


class Measure(VisitableBaseModel):
    statement: Literal["measure"] = "measure"
    qreg: QuantumRegister = None

    @property
    def qasm(self):
        return f"{self.statement};\n"


Statement = Union[Barrier, Measure]
