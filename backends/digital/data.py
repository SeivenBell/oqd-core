# External imports

from typing import Union, Optional

from pydantic import BaseModel

import pydantic_numpy.typing as pnd

########################################################################################


class TaskArgsDigital(BaseModel):
    n_shots: int = 10


class TaskResultDigital(BaseModel):
    counts: dict[str, int] = {}
    state: pnd.Np1DArray
