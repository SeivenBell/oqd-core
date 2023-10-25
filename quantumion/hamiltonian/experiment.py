from typing import List
from pydantic import BaseModel

from quantumion.hamiltonian.operator import Operator


class Experiment(BaseModel):
    sequence: List[Operator]