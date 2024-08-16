from typing import List

########################################################################################

from midstack.interface.base import TypeReflectBaseModel
from midstack.interface.atomic import Ion

########################################################################################

__all__ = [
    "Register",
]

########################################################################################


class Register(TypeReflectBaseModel):
    configuration: List[Ion]
