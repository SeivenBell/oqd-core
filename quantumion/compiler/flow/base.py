from typing import Any, List, Union

from abc import ABC, abstractmethod, abstractproperty

########################################################################################

from quantumion.compiler.analog import *
from quantumion.compiler.math import *
from quantumion.compiler.flow.traversal import *
from quantumion.compiler.flow.forward_decorators import *
from quantumion.compiler.flow.flowout import *

########################################################################################

__all__ = [
    "FlowError",
    "FlowBase",
]


########################################################################################


class FlowError(Exception):
    pass


########################################################################################


class FlowBase(ABC):
    def __init__(self, name, **kwargs):
        self.name = name
        pass

    @abstractmethod
    def __call__(self, model: Any, traversal: Traversal = Traversal()) -> "FlowOut":
        pass

    @abstractproperty
    def traversal(self) -> Union[Traversal, None]:
        pass

    pass


########################################################################################
