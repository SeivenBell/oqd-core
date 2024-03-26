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
    state: List = []#List[ComplexFloat] = [] ## need to change this back


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
