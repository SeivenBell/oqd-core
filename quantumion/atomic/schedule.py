# External imports

from pydantic import BaseModel
from typing import Union

########################################################################################


class Pulse(BaseModel):
    transitions: int  # todo: just placeholders for now


class Schedule(BaseModel):
    sequence: list[Pulse]
