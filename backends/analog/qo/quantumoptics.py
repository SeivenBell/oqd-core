#%%
import pathlib
from rich import print as pprint
import numpy as np
from juliacall import Main as jl

from backends.base import BackendBase
from backends.task import Task, TaskArgsAnalog
from quantumion.analog.circuit import AnalogCircuit


#%%
class QuantumOpticsBackend(BackendBase):
    def __init__(self):
        p = f'include("{pathlib.Path(__file__).parent.joinpath("quantumoptics.jl")}")'
        print(p)
        jl.seval(p)
        return

    def run(self, task):
        assert isinstance(task.program, AnalogCircuit), "Must be AnalogCircuit"

        circuit = task.program
        args = task.args
        print(circuit)
        result = jl.run(circuit.model_dump_json())
        return result
