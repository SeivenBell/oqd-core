from typing import Union
from pydantic import BaseModel


class Complex(BaseModel):
    real: Union[int, float]
    imag: Union[int, float]

    def __add__(self, other):
        if isinstance(other, Complex):
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
        elif isinstance(other, Complex):
            real = self.real * other.real - self.imag * self.imag
            imag = self.real * other.imag + self.imag * self.real
            return Complex(real=real, imag=imag)
        else:
            raise TypeError

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other


class Function(BaseModel):
    string: str