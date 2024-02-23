from typing import Any, List

from abc import ABC, abstractmethod, abstractproperty

########################################################################################

from quantumion.compiler.visitor import Visitor
from quantumion.compiler.analog import *

########################################################################################


class FlowBase(ABC):
    def __init__(self, name, **kwargs):
        self.name = name
        pass

    @abstractproperty
    def namespace(self):
        pass

    pass


########################################################################################


class FlowNode(FlowBase):

    @property
    def namespace(self):
        _namespace = {self.name: self}
        return _namespace


class VisitorFlowNode(FlowNode):
    def __init__(self, visitor, **kwargs):
        self.visitor = visitor
        super().__init__(**kwargs)
        pass

    def __call__(self, model: Any):
        model.accept(self.visitor)
        pass

    pass


class TransformFlowNode(VisitorFlowNode):
    def __call__(self, model: Any):
        return model.accept(self.visitor)


class FlowTerminal(FlowNode):
    pass


class FlowGraph(FlowBase):
    nodes: List[FlowBase] = [FlowTerminal(name="terminal")]
    rootnode: str = ""

    @property
    def namespace(self):
        _namespace = {self.name: self}
        for node in self.nodes:
            _namespace.update(node.namespace)
        return _namespace

    def __init__(self, max_iter=10, verbose=False, **kwargs):
        self._current_node = self.rootnode
        self._current_iter = 0
        self.max_iter = max_iter
        self.verbose = verbose
        super().__init__(**kwargs)

    @property
    def exceeded_max_iter(self):
        if self.current_iter >= self.max_iter:
            raise StopIteration
        pass

    @property
    def current_node(self):
        return self._current_node

    @property
    def current_iter(self):
        return self._current_iter

    def __iter__(self):
        self._current_node = self.rootnode
        self._current_iter = 0
        return self

    def __next__(self):
        self.exceeded_max_iter
        if isinstance(self.namespace[self.current_node], FlowTerminal):
            if self.verbose:
                print(self.current_node)
            raise StopIteration

        if self.verbose:
            print(self.current_node, end=" --> ")

        self._current_iter += 1

        return getattr(self, "next_{}".format(self.current_node))

    def __call__(self, model):
        for node in self:
            model = node(model)
        return model


class CanonicalizationFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="n0"),
        TransformFlowNode(visitor=OperatorDistribute(), name="n1"),
        TransformFlowNode(visitor=ProperOrder(), name="n2"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "n0"

    def next_n0(self, model):
        self.namespace[self.current_node](model)
        self._current_node = "n1"
        return model

    def next_n1(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "n2"
        model = _model
        return model

    def next_n2(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "terminal"
        model = _model
        return model


class TestFlow(CanonicalizationFlow):
    nodes = [
        CanonicalizationFlow(name="g1", verbose=True),
    ]
    rootnode = "g1"

    def next_g1(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "terminal"
        model = _model
        return model


# ########################################################################################

if __name__ == "__main__":
    from rich import print as pprint
    from quantumion.interface.analog import *

    I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
    A, C, J = Annihilation(), Creation(), Identity()

    op = I @ (X * (X + Y))
    fg = CanonicalizationFlow(name="g1", verbose=False)
    fg = TestFlow(name="g2", verbose=True)

    op = fg(op)
    pprint(op.accept(PrintOperator()))
