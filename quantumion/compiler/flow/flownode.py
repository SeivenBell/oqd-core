from typing import Any

########################################################################################

from quantumion.compiler.flow.base import FlowBase
from quantumion.compiler.flow.flowout import FlowOut
from quantumion.compiler.flow.traversal import Traversal

########################################################################################

__all__ = [
    "FlowNode",
    "FlowTerminal",
    "VisitorFlowNode",
    "TransformerFlowNode",
]

########################################################################################


class FlowNode(FlowBase):
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, model: Any, traversal: Traversal = Traversal()) -> FlowOut:
        raise NotImplementedError

    @property
    def traversal(self) -> None:
        return None

    pass


class FlowTerminal(FlowNode):
    def __call__(self, model: Any):
        raise NotImplementedError

    pass


class VisitorFlowNode(FlowNode):
    def __init__(self, visitor, **kwargs):
        self.visitor = visitor
        super().__init__(**kwargs)
        pass

    def __call__(self, model: Any, traversal: Traversal = Traversal()) -> FlowOut:
        emission = self.visitor.emit(model)
        return FlowOut(model=model, emission=emission)

    pass


class TransformerFlowNode(VisitorFlowNode):
    def __call__(self, model: Any, traversal: Traversal = Traversal()) -> FlowOut:
        return FlowOut(model=model.accept(self.visitor))
