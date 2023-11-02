from operator import mul
from functools import reduce
from typing import Dict, List, Literal, Tuple, Union

from pydantic import BaseModel

from quantumion.analog.coefficient import Complex
from quantumion.analog.math import levi_civita

__all__ = [
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Creation",
    "Annihilation",
    "Identity"
]


class Operator(BaseModel):
    coefficient: Union[int, float, Complex] = 1.0
    qreg: List[Literal['x', 'y', 'z', 'i']] = []
    qmode: List[List[Literal[-1, 0, 1]]] = []

    @property
    def n_qreg(self):
        return len(self.qreg)

    @property
    def n_qmode(self):
        return len(self.qmode)

    def __eq__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        eq = (self.qreg == other.qreg) and (self.qmode == other.qmode)
        return eq

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Operator(coefficient=self.coefficient * other, qreg=self.qreg, qmode=self.qmode)

        elif isinstance(other, Operator):
            qreg, phases = list(zip(*list(map(levi_civita, self.qreg, other.qreg))))
            phase = reduce(mul, phases, 1)
            coefficient = phase * self.coefficient * other.coefficient
            qmode = [a + b for a, b in zip(self.qmode, other.qmode)]
            return Operator(coefficient=coefficient, qreg=qreg, qmode=qmode)

        else:
            return TypeError

    def __rmul__(self, other):
        return self * other

    def __matmul__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        qreg = self.qreg + other.qreg
        qmode = self.qmode + other.qmode
        coefficient = self.coefficient * other.coefficient

        return Operator(coefficient=coefficient, qreg=qreg, qmode=qmode)

    def __rmatmul__(self, other):
        return other @ self


PauliX = Operator(qreg=['x'])
PauliY = Operator(qreg=['y'])
PauliZ = Operator(qreg=['z'])
PauliI = Operator(qreg=['i'])

Creation = Operator(qmode=[[-1]])
Annihilation = Operator(qmode=[[+1]])
Identity = Operator(qmode=[[0]])


if __name__ == "__main__":
    op = Operator(qreg=['x'], qmode=[[-1, 1]])
    print(op)

    print((PauliI * PauliX) @ (Creation * Annihilation))
