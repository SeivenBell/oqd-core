from pydantic import BaseModel
from typing import Union, Optional
import pydantic_numpy.typing as pnd


class TaskArgsDigital(BaseModel):
    n_shots: int = 10


class TaskResultDigital(BaseModel):
    counts: dict[int, int] = {}
    state: pnd.Np1DArray
