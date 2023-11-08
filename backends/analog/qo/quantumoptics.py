#%%
import pathlib
import json
from rich import print as pprint
import numpy as np
from juliacall import Main as jl
from juliacall import convert

from backends.base import BackendBase
from backends.task import Task, TaskArgsAnalog
from backends.analog.data import TaskResultAnalog
from quantumion.analog.circuit import AnalogCircuit


#%%
class QuantumOpticsBackend(BackendBase):
    def __init__(self):
        p = f'include("{pathlib.Path(__file__).parent.joinpath("quantumoptics.jl")}")'
        print(p)
        jl.seval(p)
        return

    def run(self, task: Task) -> TaskResultAnalog:
        assert isinstance(task.program, AnalogCircuit), "Must be AnalogCircuit"

        circuit = task.program
        args = task.args
        print(circuit)
        result_json = jl.run(task.model_dump_json())
        result = TaskResultAnalog(**json.loads(result_json))
        return result
