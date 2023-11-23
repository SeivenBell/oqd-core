from typing import Union
from pydantic import BaseModel

from quantumion.base import TypeReflectBaseModel


class Function(TypeReflectBaseModel):
    string: str
