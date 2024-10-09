from dataclasses import dataclass, field
import numpy as np
from typing import Union, List, Dict, Literal, Annotated
from pydantic import BaseModel, BeforeValidator

from oqd_compiler_infrastructure import VisitableBaseModel

########################################################################################

from ..interface.analog.operation import AnalogCircuit
from ..interface.digital.circuit import DigitalCircuit
from ..interface.atomic.circuit import AtomicCircuit

from .metric import Metric

########################################################################################


class ComplexFloat(BaseModel):
    """
    Class representing a complex number

    Attributes:
        real (float): real part of the complex number.
        imag (float): imaginary part of the complex number.
    """

    real: float
    imag: float

    @classmethod
    def cast(cls, x):
        if isinstance(x, ComplexFloat):
            return x
        if isinstance(x, complex):
            return cls(real=x.real, imag=x.imag)
        raise TypeError("Invalid type for argument x")

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


CastComplexFloat = Annotated[ComplexFloat, BeforeValidator(ComplexFloat.cast)]

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
    n_shots: Union[int, None] = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Metric] = {}


class TaskResultAnalog(VisitableBaseModel):
    """
    Contains the results of a simulation/actual experiment.

    Attributes:
        layer (str): the layer of the experiment (analog, atomic)
        times (List[float]): number of discrete times
        state (List[ComplexFloat]): Final quantum state after evolution
        metrics (Dict): metrics which have been computed for the experiment. This does not require any Measure instruction in the analog layer.
        counts (Dict[str, int]): counts of different states after the experiment. This requires Measure instruction in the analog layer.
        runtime (float): time taken for the simulation/experiment.
    """

    layer: Literal["analog"] = "analog"
    times: List[float] = []
    state: List[CastComplexFloat] = []
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
    state: List[CastComplexFloat] = []


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


class Task(VisitableBaseModel):
    """
    Class representing a task to run a quantum experiment with some arguments

    Attributes:
        program (Union[AnalogCircuit, DigitalCircuit, AtomicProgram]): Quantum experiment to run
        args (Union[TaskArgsAnalog, TaskArgsDigital, TaskArgsAtomic]): Arguments for the quantum experiment
    """

    program: Union[AnalogCircuit, DigitalCircuit, AtomicCircuit]
    args: Union[TaskArgsAnalog, TaskArgsDigital, TaskArgsAtomic]


TaskResult = Union[TaskResultAnalog, TaskResultAnalog, TaskResultDigital]

########################################################################################
