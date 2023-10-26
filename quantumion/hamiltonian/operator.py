import itertools
from pydantic import BaseModel, ValidationError

from quantumion.hamiltonian.term import Term


__all__ = [
    "Operator",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Creation",
    "Annihilation",
    "Identity"
]


class Operator(BaseModel):
    terms: list[Term]

    def check(self):
        # check that the two addends have the same number of qregs, qmodes
        assert len(set([term.n_qreg for term in self.terms])) == 1, "Inconsistent number of qregs."
        assert len(set([term.n_qmode for term in self.terms])) == 1, "Inconsistent number of qmodes."

    @property
    def n_qreg(self):
        n = list(set([term.n_qreg for term in self.terms]))
        assert len(n) == 1
        return n[0]

    @property
    def n_qmode(self):
        n = list(set([term.n_qmode for term in self.terms]))
        assert len(n) == 1
        return n[0]

    def __add__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        terms = []
        for i, term in enumerate(self.terms + other.terms):

            if term not in terms:
                terms.append(term)
            else:
                ind = terms.index(term)
                terms[ind].coefficient += term.coefficient

        out = Operator(terms=terms)
        out.check()
        return out

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            terms = [other * term for term in self.terms]

        elif isinstance(other, Operator):
            terms = []
            for term1, term2 in itertools.product(self.terms, other.terms):
                term = term1 * term2
                terms.append(term)
        else:
            raise TypeError
        return Operator(terms=terms)

    def __rmul__(self, other):
        return self * other

    def __matmul__(self, other):
        if not isinstance(other, Operator):
            raise TypeError

        terms = []
        for term1, term2 in itertools.product(self.terms, other.terms):
            term = term1 @ term2
            terms.append(term)
        return Operator(terms=terms)

    def __rmatmul__(self, other):
        return self @ other


PauliI = Operator(terms=[Term(qreg=[0])])
PauliX = Operator(terms=[Term(qreg=[1])])
PauliY = Operator(terms=[Term(qreg=[2])])
PauliZ = Operator(terms=[Term(qreg=[3])])

Creation = Operator(terms=[Term(qmode=[[-1]])])
Annihilation = Operator(terms=[Term(qmode=[[+1]])])
Identity = Operator(terms=[Term(qmode=[[0]])])
