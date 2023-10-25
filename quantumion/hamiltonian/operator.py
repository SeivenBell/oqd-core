import itertools
from pydantic import BaseModel, ValidationError

from quantumion.hamiltonian.term import Term


__all__ = [
    "Operator",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
]


class Operator(BaseModel):
    terms: list[Term]

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

        return Operator(terms=terms)

    def __mul__(self, other):

        if isinstance(other, (int, float, complex)):
            terms = [other * term.coefficient for term in self.terms]

        elif isinstance(other, Operator):
            terms = []
            for term1, term2 in itertools.product(self.terms, other.terms):
                term = term1 * term2
                terms.append(term)
        else:
            raise TypeError
        return Operator(terms=terms)


PauliI = Operator(terms=[Term(qreg=[0])])
PauliX = Operator(terms=[Term(qreg=[1])])
PauliY = Operator(terms=[Term(qreg=[2])])
PauliZ = Operator(terms=[Term(qreg=[3])])

Create = Operator(terms=[Term(qmode=[-1])])
Annihilation = Operator(terms=[Term(qmode=[+1])])
Identity = Operator(terms=[Term(qmode=[0])])