import itertools
from typing import List, Union, Optional
from pydantic import BaseModel, ValidationError

from quantumion.analog.operator import Operator
from quantumion.analog.dissipation import Dissipation


__all__ = [
    "AnalogGate",
]


class AnalogGate(BaseModel):
    duration: float = None
    hamiltonian: list[Operator] = []
    dissipation: list[Dissipation] = []

    def check(self):
        # check that the two addends have the same number of qregs, qmodes
        assert (
                len(set([term.n_qreg for term in self.hamiltonian])) == 1
        ), "Inconsistent number of qregs."
        assert (
                len(set([term.n_qmode for term in self.hamiltonian])) == 1
        ), "Inconsistent number of qmodes."

    @property
    def n_qreg(self):
        n = list(set([term.n_qreg for term in self.hamiltonian]))
        assert len(n) == 1
        return n[0]

    @property
    def n_qmode(self):
        n = list(set([term.n_qmode for term in self.hamiltonian]))
        assert len(n) == 1
        return n[0]

    def __add__(self, other):
        if not isinstance(other, AnalogGate):
            raise TypeError

        terms = []
        for i, term in enumerate(self.hamiltonian + other.hamiltonian):
            if term not in terms:
                terms.append(term)
            else:
                ind = terms.index(term)
                terms[ind].coefficient += term.coefficient

        out = AnalogGate(terms=terms)  # todo: fix dunder operators on AnalogGate
        out.check()
        return out

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            terms = [other * term for term in self.hamiltonian]

        elif isinstance(other, AnalogGate):
            terms = []
            for term1, term2 in itertools.product(self.hamiltonian, other.hamiltonian):
                term = term1 * term2
                terms.append(term)
        else:
            raise TypeError
        return AnalogGate(terms=terms)

    def __rmul__(self, other):
        return self * other

    def __matmul__(self, other):
        if not isinstance(other, AnalogGate):
            raise TypeError

        terms = []
        for term1, term2 in itertools.product(self.hamiltonian, other.hamiltonian):
            term = term1 @ term2
            terms.append(term)
        return AnalogGate(terms=terms)

    def __rmatmul__(self, other):
        return self @ other
