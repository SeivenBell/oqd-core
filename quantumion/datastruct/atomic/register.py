from typing import List

########################################################################################

from quantumion.datastruct.base import TypeReflectBaseModel
from quantumion.datastruct.atomic import Ion

########################################################################################

__all__ = [
    "Register",
]

########################################################################################


class Register(TypeReflectBaseModel):
    configuration: List[Ion]
