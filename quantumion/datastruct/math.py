import numpy as np

########################################################################################

from quantumion.datastruct.base import VisitableBaseModel

########################################################################################


class ComplexFloat(VisitableBaseModel):
    real: float
    imag: float

    @classmethod
    def from_np_complex128(cls, np_complex128):
        """Converts a numpy complex128 datatype to custom ComplexFloat"""
        return cls(real=np_complex128.real, imag=np_complex128.imag)

    def __add__(self, other):
        if isinstance(other, ComplexFloat):
            self.real += other.real
            self.imag += other.imag
            return self

        elif isinstance(other, (float, int)):
            self.real += other
            return self

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            self.real *= other
            self.imag *= other
            return self
        elif isinstance(other, ComplexFloat):
            real = self.real * other.real - self.imag * self.imag
            imag = self.real * other.imag + self.imag * self.real
            return ComplexFloat(real=real, imag=imag)
        else:
            raise TypeError

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other


class Function(VisitableBaseModel):
    string: str
