from pydantic import BaseModel
from typing import Union

from quantumion.analog.circuit import AnalogCircuit
from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import Schedule

from backends.analog.data import TaskArgsAnalog, TaskResultAnalog
from backends.digital.data import TaskArgsDigital, TaskResultDigital


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, Schedule]
    args: Union[TaskArgsAnalog, TaskArgsDigital]
