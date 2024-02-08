from operator import mul
from functools import reduce
from typing import List, Literal, Union

########################################################################################

from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.math import ComplexFloat
from quantumion.utils.math import levi_civita

########################################################################################

__all__ = [
    "Operator",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Creation",
    "Annihilation",
    "Identity",
]

########################################################################################


class Operator(VisitableBaseModel):
    """
    Examples:
        >>> PauliX = Operator(coefficient=1.0, pauli=["x"])
        >>> Destroy = Operator(coefficient=1.0, ladder=[[-1]])
        >>> Create = Operator(coefficient=1.0, ladder=[[1]])

    Args:
        coefficient (int, float, ComplexFloat): time-independent coefficient of the operator
        pauli (list["x", "y", "z", "i"]): Pauli operator on qubit index
        ladder (list[list[-1, 0, +1]]): Ladder operator(s) on mode index
    """

    coefficient: Union[int, float, ComplexFloat] = 1.0
    pauli: List[Literal["x", "y", "z", "i"]] = []
    ladder: List[List[Literal[-1, 0, 1]]] = []

    @property
    def n_qreg(self):
        return len(self.pauli)

    @property
    def n_qmode(self):
        return len(self.ladder)

    def __eq__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        eq = (self.pauli == other.pauli) and (self.ladder == other.ladder)
        return eq

    # def __add__(self, other):
    #     if not isinstance(other, Operator):
    #         raise TypeError(f"unsupported operand types for '{type(self)}' and '{type(other)}'")
    #
    #     assert (self.n_qreg == other.n_qreg) and (self.n_qmode == self.n_qmode)
    #
    #     if (self.qreg == other.qreg) and (self.qmode == other.qmode):
    #         coefficient = self.coefficient + other.coefficient
    #         return Operator(coefficient=coefficient, qreg=self.qreg, qmode=self.qmode)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Operator(
                coefficient=self.coefficient * other,
                pauli=self.pauli,
                ladder=self.ladder,
            )

        elif isinstance(other, Operator):
            qreg, phases = list(zip(*list(map(levi_civita, self.pauli, other.pauli))))
            phase = reduce(mul, phases, 1)
            coefficient = phase * self.coefficient * other.coefficient
            qmode = [a + b for a, b in zip(self.ladder, other.ladder)]
            return Operator(coefficient=coefficient, pauli=qreg, ladder=qmode)

        else:
            return TypeError

    def __rmul__(self, other):
        return self * other

    def __matmul__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        qreg = self.pauli + other.pauli
        qmode = self.ladder + other.ladder
        coefficient = self.coefficient * other.coefficient

        return Operator(coefficient=coefficient, pauli=qreg, ladder=qmode)

    def __rmatmul__(self, other):
        return other @ self


PauliX = Operator(pauli=["x"])
PauliY = Operator(pauli=["y"])
PauliZ = Operator(pauli=["z"])
PauliI = Operator(pauli=["i"])

Creation = Operator(ladder=[[-1]])
Annihilation = Operator(ladder=[[1]])
Identity = Operator(ladder=[[0]])


if __name__ == "__main__":
    op = Operator(pauli=["x"], ladder=[[-1, 1]])
    print(op)

    print((PauliI * PauliX) @ (Creation * Annihilation))
