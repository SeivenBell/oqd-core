# External imports

from typing import Union

from quantumion.base import TypeReflectBaseModel

########################################################################################


class Dissipation(TypeReflectBaseModel):
    jumps: int = None  # todo: discuss ir for dissipation
