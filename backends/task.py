from dataclasses import dataclass, field
import numpy as np
from pydantic import BaseModel
from typing import Union, List, Optional, Dict
from pydantic_numpy import typing as pnd

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.operator import Operator
from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import AtomicProgram

from backends.metric import Metric
# from backends.metric import Expectation, EntanglementEntropyVN, EntanglementEntropyReyni


@dataclass
class DataAnalog:
    times: np.array = field(default_factory=lambda: np.empty(0))
    state: np.array = field(default_factory=lambda: np.empty(0))
    metrics: dict[str, List[Union[float, int]]] = field(default_factory=dict)
    shots: np.array = field(default_factory=lambda: np.empty(0))


class TaskArgsAnalog(BaseModel):
    n_shots: int = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Metric] = {}

    class Config:
        extra = "forbid"


class TaskResultAnalog(BaseModel):
    counts: dict[int, int] = {}
    times: list[float] = []
    state: pnd.Np1DArray = None
    runtime: float = None
    metrics: dict[str, List[Union[float, int]]] = {}


class TaskArgsDigital(BaseModel):
    repetitions: int = 10

    class Config:
        extra = "forbid"


class TaskResultDigital(BaseModel):
    counts: dict[str, int] = {}
    state: pnd.Np1DArray


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, AtomicProgram]
    args: Union[TaskArgsAnalog, TaskArgsDigital]
