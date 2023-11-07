# External imports

from pydantic import BaseModel
from typing import Union

########################################################################################

# Internal exports

from backends.analog.data import TaskArgsAnalog
from backends.digital.data import TaskArgsDigital

from quantumion.analog.circuit import AnalogCircuit
from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import AtomicProgram

########################################################################################


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, AtomicProgram]
    args: Union[TaskArgsAnalog, TaskArgsDigital]
