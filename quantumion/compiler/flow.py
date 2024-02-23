from typing import Any, List

from abc import ABC, abstractmethod, abstractproperty

########################################################################################

from quantumion.compiler.visitor import Visitor
from quantumion.compiler.analog import *
from quantumion.compiler.math import *

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

    @abstractmethod
    def __call__(self, model: Any):
        pass


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
    def __call__(self, model: Any):
        raise NotImplementedError

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

    def __init__(self, max_iter=1000, verbose=False, **kwargs):
        self._current_node = self.rootnode
        self._current_iter = 0
        self.max_iter = max_iter
        self.verbose = verbose
        super().__init__(**kwargs)

    @property
    def exceeded_max_iter(self):
        if self.current_iter >= self.max_iter:
            raise RecursionError
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
                print("({}: {})".format(self.current_iter, self.current_node))
            raise StopIteration

        if self.verbose:
            print("({}: {})".format(self.current_iter, self.current_node), end=" --> ")

        self._current_iter += 1

        return getattr(self, "next_{}".format(self.current_node))

    def __call__(self, model):
        for node in self:
            model = node(model)
        return model


class CanonicalizationFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="hspace"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformFlowNode(visitor=ProperOrder(), name="proper"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformFlowNode(visitor=GatherPauli(), name="gatherpauli"),
        TransformFlowNode(visitor=PruneIdentity(), name="prune"),
        TransformFlowNode(visitor=PauliAlgebra(), name="paulialgebra"),
        TransformFlowNode(visitor=NormalOrder(), name="normal"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute2"),
        TransformFlowNode(visitor=ProperOrder(), name="proper2"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath2"),
        TransformFlowNode(visitor=SortedOrder(), name="sorted"),
        TransformFlowNode(visitor=PartitionMathExpr(), name="partmath"),
        TransformFlowNode(visitor=DistributeMathExpr(), name="distmath"),
        TransformFlowNode(visitor=ProperOrderMathExpr(), name="propermath"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "hspace"

    def next_hspace(self, model):
        self.namespace[self.current_node](model)
        self._current_node = "distribute"
        return model

    def next_distribute(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "proper"
        model = _model
        return model

    def next_proper(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "gathermath"
        model = _model
        return model

    def next_gathermath(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "gatherpauli"
        model = _model
        return model

    def next_gatherpauli(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "paulialgebra"
        model = _model
        return model

    def next_paulialgebra(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "normal"
        model = _model
        return model

    def next_normal(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "sorted"
        else:
            self._current_node = "distribute2"
        model = _model
        return model

    def next_distribute2(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "proper2"
        model = _model
        return model

    def next_proper2(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "gathermath2"
        model = _model
        return model

    def next_gathermath2(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "normal"
        model = _model
        return model

    def next_sorted(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "distmath"
        model = _model
        return model

    def next_distmath(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "propermath"
        model = _model
        return model

    def next_propermath(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "partmath"
        model = _model
        return model

    def next_partmath(self, model):
        _model = self.namespace[self.current_node](model)
        if model == _model:
            self._current_node = "terminal"
        model = _model
        return model


# ########################################################################################

if __name__ == "__main__":
    from rich import print as pprint
    from quantumion.interface.analog import *
    from quantumion.interface.math import *

    I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
    A, C, J = Annihilation(), Creation(), Identity()

    # op = I @ (MathStr(string="1*(a+b)") * (X * (X + Y))) @ (A * A * C)
    op = X @ (A * C) @ Y
    fg = CanonicalizationFlow(name="g1", verbose=True)

    op = fg(op)
    pprint(op.accept(PrintOperator()))
