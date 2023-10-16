from __future__ import annotations

import warnings
from typing import Union

import numexpr as ne


class CoefficientBase(object):
    def __init__(self):
        return

    def __str__(self):
        s = "base coefficient"
        return s

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return NotImplementedError

    def __mul__(self, other):
        return NotImplementedError

    def __matmul__(self, other):
        return NotImplementedError

    def __truediv__(self, other):
        return NotImplementedError

    def __pow__(self, power, modulo=None):
        return NotImplementedError

    # def __eq__(self, other):
    #     return NotImplementedError
    # def __neq__(self, other):
    #     return NotImplementedError

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


class StringCoefficient(CoefficientBase):
    def __init__(self, expr_str: str, expr_par: dict | None = None):
        super().__init__()
        if not isinstance(expr_str, str):
            raise TypeError("Expression must be a string-type.")

        if expr_par is None:
            expr_par = {}
        if not isinstance(expr_par, dict):
            raise TypeError("Expression parameters must be dictionary-type.")
        if "t" in expr_par.values():
            raise PermissionError("t is a protected symbol.")

        self.expr_str = expr_str
        self.expr_par = expr_par
        return

    def numeric(self, t):
        return ne.evaluate(
            self.expr_str, local_dict=self.expr_par, global_dict={"t": t}
        )

    def __str__(self):
        return f"expr: {self.expr_str}  |  pars: {(str(self.expr_par) if self.expr_par else '')}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _combine_pars(self, other):
        expr_par = {}
        for _expr_par in (self, other):
            if any(key in expr_par for key in _expr_par.keys()):
                warnings.warn(
                    "String coefficient parameters have a colliding key. "
                    "Default behaviour is to treat them as the same parameter.",
                    RuntimeWarning,
                )
            if isinstance(_expr_par, dict):
                expr_par.update(_expr_par)
        return expr_par

    @staticmethod
    def _combine_strs(self, other, symbol):
        if symbol not in ("+", "-", "*", "/", "**"):
            raise RuntimeError("Not a valid string symbol.")
        expr_str = "".join(["(", self, f") {symbol} (", other, ")"])
        return expr_str

    def __add__(self, other):
        try:
            if isinstance(other, StringCoefficient):
                expr_str = self._combine_strs(self.expr_str, other.expr_str, "+")
                expr_par = self._combine_pars(self.expr_par, other.expr_par)

            elif isinstance(other, (str, int, float, complex)):
                expr_str = self._combine_strs(self.expr_str, str(other), "+")
                expr_par = self.expr_par

            else:
                raise TypeError

            out = StringCoefficient(expr_str=expr_str, expr_par=expr_par)
            return out

        except TypeError:
            return other.__mul__(self)

    def __mul__(self, other):
        try:
            if isinstance(other, StringCoefficient):
                expr_str = self._combine_strs(self.expr_str, other.expr_str, "*")
                expr_par = self._combine_pars(self.expr_par, other.expr_par)

            elif isinstance(other, (str, int, float, complex)):
                if other == 1 or other == 1.0:
                    expr_str = self.expr_str
                else:
                    expr_str = self._combine_strs(self.expr_str, str(other), "*")
                expr_par = self.expr_par

            else:
                raise TypeError

            out = StringCoefficient(expr_str=expr_str, expr_par=expr_par)
            return out

        except TypeError:
            return other.__mul__(self)

    def __truediv__(self, other):
        try:
            if isinstance(other, StringCoefficient):
                expr_str = self._combine_strs(self.expr_str, other.expr_str, "/")
                expr_par = self._combine_pars(self.expr_par, other.expr_par)

            elif isinstance(other, (str, int, float, complex)):
                expr_str = self._combine_strs(self.expr_str, str(other), "/")
                expr_par = self.expr_par

            else:
                raise TypeError

            out = StringCoefficient(expr_str=expr_str, expr_par=expr_par)
            return out

        except TypeError:
            return other.__truediv__(self)

    def __matmul__(self, other):
        return NotImplementedError("@ operator not defined for string coefficients.")

    def __pow__(self, power, modulo=None):
        if isinstance(power, StringCoefficient):
            expr_str = self._combine_strs(self.expr_str, power.expr_str, "**")
            expr_par = self._combine_pars(self.expr_par, power.expr_par)

        elif isinstance(power, (str, int, float)):
            # todo: support complex powers
            expr_str = self._combine_strs(self.expr_str, str(power), "**")
            expr_par = self.expr_par

        else:
            raise TypeError("Power only implemented between StringCoefficient types.")

        out = StringCoefficient(expr_str=expr_str, expr_par=expr_par)
        return out


# todo: remove function strings below
# cython_strings = [
#     "abs",
#     "acos",
#     "acosh",
#     "arg",
#     "asin",
#     "asinh",
#     "atan",
#     "atanh",
#     "conj",
#     "cos",
#     "cosh",
#     "exp",
#     "erf",
#     "zerf",
#     "imag",
#     "log",
#     "log10",
#     "norm",
#     "pi",
#     "proj",
#     "real",
#     "sin",
#     "sinh",
#     "sqrt",
#     "tan",
#     "tanh",
# ]
