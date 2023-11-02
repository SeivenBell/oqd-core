from typing import Union
from pydantic import BaseModel


class Dissipation(BaseModel):
    jumps: int = None   # todo: discuss ir for dissipation
