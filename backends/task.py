# External imports
from dataclasses import dataclass, field

import numpy as np
from pydantic import BaseModel
from typing import Union, List

from pydantic_numpy import typing as pnd


from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.operator import Operator

from quantumion.digital.circuit import DigitalCircuit

from quantumion.atomic.schedule import AtomicProgram


@dataclass
class DataAnalog:
    times: np.array = None
    state: np.array = None
    expect: dict[str, Union[int, float]] = field(default_factory=dict)
    shots: np.array = None


class TaskArgsAnalog(BaseModel):
    n_shots: int = 10
    fock_cutoff: int = 4
    observables: dict[str, Operator] = {}
    dt: float = 0.1


class TaskResultAnalog(BaseModel):
    counts: dict[int, int] = {}
    expect: dict[str, List[Union[float, int]]] = {}
    times: list[float] = []
    state: pnd.Np1DArray = None
    runtime: float = None


class TaskArgsDigital(BaseModel):
    n_shots: int = 10


class TaskResultDigital(BaseModel):
    counts: dict[str, int] = {}
    state: pnd.Np1DArray


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, AtomicProgram]
    args: Union[TaskArgsAnalog, TaskArgsDigital]

