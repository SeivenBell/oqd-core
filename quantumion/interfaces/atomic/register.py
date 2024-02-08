from typing import List

########################################################################################

from quantumion.interfaces.base import TypeReflectBaseModel
from quantumion.interfaces.atomic import Ion

########################################################################################

__all__ = [
    "Register",
]

########################################################################################


class Register(TypeReflectBaseModel):
    configuration: List[Ion]
