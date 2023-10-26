from typing import List
from pydantic import BaseModel

from quantumion.hamiltonian.operator import Operator


class Experiment(BaseModel):
    sequence: List[Operator] = []
    n_qreg: int = None
    n_qmode: int = None

    def add(self, operator: Operator):
        if operator.n_qreg != self.n_qreg and self.n_qreg is not None:
            raise ValueError("Inconsistent qreg dimensions.")
        if operator.n_qmode != self.n_qmode and self.n_qmode is not None:
            raise ValueError("Inconsistent qmode dimensions.")

        self.sequence.append(operator)
        self.n_qreg = operator.n_qreg
        self.n_qmode = operator.n_qmode


