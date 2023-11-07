#%%
from rich import print as pprint
import numpy as np
from juliacall import Main as jl
from typing import List

from pydantic import BaseModel


#%%
class AnalogGate(BaseModel):
    duration: int = 1


class AnalogCircuit(BaseModel):
    sequence: List[AnalogGate] = []
    n_qreg: int = None


#%%
c = AnalogCircuit(sequence=[AnalogGate()], n_qreg=1)
pprint(c)

#%%
jl.seval('include("./QOJulia.jl")')

#%%
jl.test_analog_circuit(c.model_dump_json())

#%%
