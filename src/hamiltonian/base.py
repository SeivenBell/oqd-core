import copy
import functools
import itertools
import operator
from typing import List, Dict

import numpy as np

from quantumion.hamiltonian.coefficients import StringCoefficient


class Operator(object):
    """
    Base class for all operators.
    """

    def __init__(self):
        self._data = []
        return

    @classmethod
    def load(cls, d: List[List[Dict]]):
        op = cls()
        # todo: check semantics of d
        op._data = d
        return op

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, d):
        raise NotImplementedError("Cannot set the data directly.")

    @property
    def dim_qreg(self):
        return len(self.data[0][1]["qreg"])

    @property
    def dim_qmode(self):
        return len(self.data[0][1]["qmode"])

    def __str__(self):
        s = "["
        for i, (c, t) in enumerate(self.data):
            s += f"({c}: " + "{"
            for j, (key, value) in enumerate(t.items()):
                s += f"{key}: {value}"
                if j+1 < len(t):
                    s += ", "
            s += "})"
            if i+1 < len(self.data):
                s += ","
        s += "]"
        return s

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not (isinstance(self, Operator) and isinstance(other, Operator)):
            raise TypeError(
                f"unsupported type for + between {type(self)} and {type(other)}"
            )

        out = Operator()
        coeffs, terms = [], []

        if (
            not len(
                set(
                    [len(d["qreg"]) for (_, d) in self.data]
                    + [len(d["qreg"]) for (_, d) in other.data]
                )
            )
            == 1
        ):
            raise TypeError("Mismatched dimensions in qreg operators when adding.")

        if (
            not len(
                set(
                    [len(d["qmode"]) for (_, d) in self.data]
                    + [len(d["qmode"]) for (_, d) in other.data]
                )
            )
            == 1
        ):
            raise TypeError(
                "Mismatched dimensions in qmode operators when adding."
            )

        for data in (self.data, other.data):
            for c, t in data:
                if t not in terms:
                    if c != 0:
                        coeffs.append(c)
                        terms.append(t)
                else:
                    ind = terms.index(t)
                    coeffs[ind] += c

        out._data = list(zip(coeffs, terms))
        return out

    def __matmul__(self, other):
        if not (isinstance(self, Operator) and isinstance(other, Operator)):
            raise TypeError(
                f"unsupported type for @ between {type(self)} and {type(other)}"
            )

        out = Operator()
        combinations = itertools.product(self.data, other.data)

        coeffs, terms = [], []
        for (c1, t1), (c2, t2) in combinations:
            t = dict()

            # pauli operators
            t["qreg"] = t1["qreg"] + t2["qreg"]

            # fock basis operators
            t["qmode"] = t1["qmode"] + t2["qmode"]

            c = c1 * c2
            if t not in terms:
                if c != 0:
                    coeffs.append(c)
                    terms.append(t)
            else:
                ind = terms.index(t)
                coeffs[ind] += c

        out._data = list(zip(coeffs, terms))
        return out

    def __mul__(self, other):
        out = Operator()

        if isinstance(
            other, (int, float, complex, np.integer, np.floating, StringCoefficient)
        ):
            coeffs, terms = [], []
            for c, t in self._data:
                c = c * other
                if c != 0:
                    coeffs.append(c)
                    terms.append(t)

            out._data = list(zip(coeffs, terms))
            return out

        elif isinstance(other, Operator):
            # todo: some potential bugs here in the coefficients due to the order of multiplication?
            combinations = itertools.product(self.data, other.data)
            coeffs, terms = [], []
            for (c1, t1), (c2, t2) in combinations:
                c = c1 * c2
                t = {"qreg": [], "qmode": []}
                # pauli operators
                for a, b in zip(t1["qreg"], t2["qreg"]):
                    # evaluates qreg operator logic (\delta_ij I + 1j \epsilon_{ijk} \sigma_k)
                    t_i = (abs(a - b) + (0 if a * b != 2 else 2)) % 4
                    c_i = (
                        1
                        if any([i == 0 for i in (t_i, a, b)])
                        else (1j if (b - a) in (1, -2) else -1j)
                    )
                    t["qreg"].append(t_i)
                    c *= c_i

                # ladder operator
                for a, b in zip(t1["qmode"], t2["qmode"]):
                    # lists of integers representing ladder operator terms are concatenated
                    t["qmode"].append(a + b)

                if t not in terms:
                    if c != 0:
                        coeffs.append(c)
                        terms.append(t)
                else:
                    ind = terms.index(t)
                    coeffs[ind] += c

            data = list(zip(coeffs, terms))
            out._data = data
            return out

        else:
            return NotImplementedError(
                "Multiplication between operators not implemented."
            )

    def __truediv__(self, other):
        if isinstance(
            other, (int, float, complex, np.integer, np.floating, np.complexfloating)
        ):
            out = Operator()
            for c, t in self._data:
                out._data.append((c / other, t))
            return out
        else:
            return TypeError("Division only valid for int, float, and complex type.")

    def __pow__(self, power, modulo=None):
        if isinstance(power, int) and power > 0:
            out = functools.reduce(operator.mul, power * [self])
            return out
        else:
            raise TypeError("Operators can only be raised to positive integer powers.")

    def __eq__(self, other):
        if isinstance(other, Operator):
            tmp1 = copy.copy(other.data)
            tmp2 = copy.copy(self.data)
            # check if all terms in both operators
            ind1, ind2 = [], []
            for i, (c1, t1) in enumerate(tmp1):
                for j, (c2, t2) in enumerate(tmp2):
                    if t1 == t2 and c1 == c2:
                        ind1.append(i)
                        ind2.append(j)
                        continue

            tmp1 = [t for i, t in enumerate(tmp1) if i not in ind1]
            tmp2 = [t for j, t in enumerate(tmp2) if j not in ind2]

            if not tmp1 and not tmp2:
                # both lists empty, operators have all the same terms & are therefore equal
                return True
            else:
                return False
        else:
            return False

    def __neq__(self, other):
        return not (self == other)

    def is_hermitian(self):
        if self == self.dagger():
            return True
        else:
            return False

    def __rmatmul__(self, other):
        return self @ other

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __neg__(self):
        return -1 * self

    def dagger(self):
        out = Operator()
        coeffs, terms = [], []
        for c1, t1 in self.data:
            t = dict()

            t["qreg"] = t1["qreg"]
            t["qmode"] = []
            for a in t1["qmode"]:
                t["qmode"].append(tuple([-1 * i for i in reversed(a)]))

            c = np.conjugate(c1)

            coeffs.append(c)
            terms.append(t)

        out._data = list(zip(coeffs, terms))
        return out

    def to_string(self):
        qreg_map = {0: "I", 1: "X", 2: "Y", 3: "Z"}
        qmode_map = {0: "I", -1: "a", +1: "at"}

        s = ""
        for coeff, term in self._data:
            s += " + "
            s += f"{coeff} * "
            s += ".".join([f"{qreg_map[p]}" for p in term["qreg"]])
            s += " | "
            s += ".".join([f"{''.join([qmode_map[fi] for fi in f])}" for f in term["qmode"]])
        return s

    def mathtype(self, term):
        qreg_map = {
            0: r"\mathcal{1}",
            1: r"\hat{\sigma}_x",
            2: r"\hat{\sigma}_y",
            3: r"\hat{\sigma}_z",
        }
        qmode_map = {0: r"\mathcal{1}", -1: r"\hat{a}", +1: r"\hat{a}^\dagger"}
        texify = lambda symbol, reg: f"{symbol}"
        sep = r"\otimes "

        s = ""
        if term["qreg"]:
            s += f"{sep}".join(
                [texify(qreg_map[p], reg) for (reg, p) in enumerate(term["qreg"])]
            )
        if term["qmode"]:
            s += f"{sep}"
            s += f"{sep}".join(
                [
                    texify(" ".join([qmode_map[fi] for fi in f]), reg)
                    for (reg, f) in enumerate(term["qmode"])
                ]
            )
        return s

    def to_mathtype(self):
        s = "$"
        for i, (coeff, term) in enumerate(self._data):
            s += " + " if i != 0 else ""
            s += f"{coeff}"
            s += r"\times "
            s += self.mathtype(term)
        s += "$"
        return s

    def to_latex(self):
        from IPython.display import display, Math
        s = self.to_mathtype()
        s = "$" + s + "$"
        return display(Math(r"{}".format(s)))
