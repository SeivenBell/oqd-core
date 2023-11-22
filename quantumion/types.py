import numpy as np

from quantumion.base import TypeReflectBaseModel


class ComplexFloat(TypeReflectBaseModel):
    re: float
    im: float

    @classmethod
    def from_np_complex128(cls, np_complex128):
        """Converts a numpy complex128 datatype to custom ComplexFloat"""
        return cls(re=np_complex128.real, im=np_complex128.imag)
