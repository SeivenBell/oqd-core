from operator import mul
from functools import reduce
from typing import Annotated, Dict, List, Literal, Tuple, Union
from typing_extensions import Annotated

from pydantic import BaseModel, ValidationError
from pydantic.functional_validators import AfterValidator

from quantumion.hamiltonian.coefficients import Complex


def validate_pauli_int(v: int):
    assert 0 <= v <= 3, f"Qubit pauli integer must be in range [0, 3]"
    return v


def validate_qmode_int(v: int):
    assert v in (-1, 0, 1), f"Qmode ladder operator integer must be one of (-1, 0, +1)"
    return v


class Term(BaseModel):
    coefficient: Union[int, float, Complex] = 1.0
    qreg: List[Annotated[int, AfterValidator(validate_pauli_int)]] = []
    qmode: List[List[Annotated[int, AfterValidator(validate_qmode_int)]]] = []

    @property
    def n_qreg(self):
        return len(self.qreg)

    @property
    def n_qmode(self):
        return len(self.qmode)

    def __eq__(self, other):
        if not isinstance(other, Term):
            raise TypeError

        eq = (self.qreg == other.qreg) and (self.qmode == other.qmode)
        return eq

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Term(coefficient=self.coefficient * other, qreg=self.qreg, qmode=self.qmode)

        elif isinstance(other, Term):
            def lc(j, k):
                if j == 0 or k == 0:
                    return j + k
                if j == k:
                    return 0
                else:
                    return (j + k) % 4

            def lc_phase(j, k):
                if j == k or j == 0 or k == 0:
                    return 1
                elif j < k:
                    return Complex(real=0, imag=-1)
                elif j > k:
                    return Complex(real=0, imag=+1)

            phases = list(map(lc_phase, self.qreg, other.qreg))
            phase = reduce(mul, phases, 1)
            coefficient = phase * self.coefficient * other.coefficient
            qreg = [lc(j, k) for (j, k) in zip(self.qreg, other.qreg)]
            # qmode = [0 for (a, b) in zip(self.qmode, other.qmode)]
            qmode = [a + b for a, b in zip(self.qmode, other.qmode)]
            return Term(coefficient=coefficient, qreg=qreg, qmode=qmode)

        else:
            return TypeError

    def __rmul__(self, other):
        return self * other

    def __matmul__(self, other):
        if not isinstance(other, Term):
            raise TypeError

        qreg = self.qreg + other.qreg
        qmode = self.qmode + other.qmode
        coefficient = self.coefficient * other.coefficient

        return Term(coefficient=coefficient, qreg=qreg, qmode=qmode)