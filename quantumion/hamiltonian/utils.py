import functools
import operator

from quantumion.hamiltonian.operator import Operator


def sum(args) -> Operator:
    return functools.reduce(operator.add, args)


def prod(args) -> Operator:
    return functools.reduce(operator.mul, args)


def tensor(args) -> Operator:
    return functools.reduce(operator.matmul, args)
