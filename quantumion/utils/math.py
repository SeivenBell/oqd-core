import functools
import operator

from quantumion.datastruct.math import ComplexFloat


def sum(args):
    return functools.reduce(operator.add, args)


def prod(args):
    return functools.reduce(operator.mul, args)


def tensor(args):
    return functools.reduce(operator.matmul, args)


_lc = {
    "ii": ("i", +1),
    "ix": ("x", +1),
    "iy": ("y", +1),
    "iz": ("z", +1),
    "xi": ("x", +1),
    "xx": ("i", +1),
    "xy": ("z", ComplexFloat(real=0, imag=+1)),
    "xz": ("y", ComplexFloat(real=0, imag=-1)),
    "yi": ("y", +1),
    "yx": ("z", ComplexFloat(real=0, imag=+1)),
    "yy": ("i", +1),
    "yz": ("x", ComplexFloat(real=0, imag=-1)),
    "zi": ("z", +1),
    "zx": ("y", ComplexFloat(real=0, imag=-1)),
    "zy": ("x", ComplexFloat(real=0, imag=+1)),
    "zz": ("i", +1),
}


def levi_civita(a, b):
    return _lc.get(a + b, None)
