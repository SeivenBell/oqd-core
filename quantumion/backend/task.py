from dataclasses import dataclass, field
import numpy as np
from typing import Union, List, Dict, Literal
from pydantic import BaseModel, ConfigDict
from quantumion.interface.base import VisitableBaseModel
import qutip as qt

########################################################################################

#from quantumion.interface.math import ComplexFloat
from quantumion.interface.analog.operations import AnalogCircuit
from quantumion.interface.digital.circuit import DigitalCircuit
from quantumion.interface.atomic.program import AtomicProgram

from quantumion.backend.metric import Metric

########################################################################################

class ComplexFloat(BaseModel):
    real: float
    imag: float

    @classmethod
    def cast_from_np_complex128(cls, np_complex128):
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
########################################################################################

@dataclass
class DataAnalog:
    times: np.array = field(default_factory=lambda: np.empty(0))
    state: np.array = field(default_factory=lambda: np.empty(0))
    metrics: dict[str, List[Union[float, int]]] = field(default_factory=dict)
    shots: np.array = field(default_factory=lambda: np.empty(0))


########################################################################################sss


class TaskArgsAnalog(VisitableBaseModel):
    layer: Literal["analog"] = "analog"
    n_shots: int = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Metric] = {}


class TaskResultAnalog(VisitableBaseModel):
    layer: Literal["analog"] = "analog"
    times: List[float] = []
    state: List = None # list of complex float
    metrics: Dict[str, List[Union[float, int]]] = {}
    counts: Dict[str, int] = {}
    runtime: float = None


########################################################################################


class TaskArgsDigital(BaseModel):
    layer: Literal["digital"] = "digital"
    repetitions: int = 10


class TaskResultDigital(BaseModel):
    layer: Literal["digital"] = "digital"
    counts: dict[str, int] = {}
    state: List[ComplexFloat] = []


########################################################################################


class TaskArgsAtomic(BaseModel):
    layer: Literal["atomic"] = "atomic"
    n_shots: int = 10
    fock_trunc: int = 4
    dt: float = 0.1


class TaskResultAtomic(BaseModel):
    layer: Literal["atomic"] = "atomic"
    # Hardware results
    collated_state_readout: dict[int, int] = {}
    state_readout: dict[int, int] = {}


########################################################################################


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, AtomicProgram]
    args: Union[TaskArgsAnalog, TaskArgsDigital, TaskArgsAtomic]


TaskResult = Union[TaskResultAnalog, TaskResultAnalog, TaskResultDigital]

########################################################################################
