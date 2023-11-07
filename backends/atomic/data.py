# External imports

from dataclasses import dataclass, field

from typing import Union, List

from pydantic import BaseModel

import pydantic_numpy.typing as pnd

import numpy as np

########################################################################################

# Internal imports


########################################################################################


class TaskArgsAtomic(BaseModel):
    n_shots: int = 10
    fock_trunc: int = 4
    dt: float = 0.1


class TaskResultAtomic(BaseModel):
    # Hardware results
    collated_state_readout: dict[int, int] = {}
    state_readout: dict[int, int] = {}
    detector_counts: dict[int, pnd.NpNDArrayInt32] = {}
