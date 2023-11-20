from pydantic import BaseModel
import numpy as np


class ComplexFloat(BaseModel):
    re: float
    im: float

    @classmethod
    def from_np_complex128(cls, np_complex128):
        """ Converts a numpy complex128 datatype to custom ComplexFloat """
        return cls(re=np_complex128.real, im=np_complex128.imag)