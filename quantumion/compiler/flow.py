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

        return getattr(self, "forward_{}".format(self.current_node))

    def __call__(self, model):
        for node in self:
            model = node(model)
        return model

    def forward_factory(method):
        def _method(self, model: Any):
            _model = self.namespace[self.current_node](model)

            instructions = method(self, model)

            if model == _model:
                self._current_node = instructions["done"]
            elif "repeat" in instructions.keys():
                self._current_node = instructions["repeat"]

            model = _model
            return model

        return _method


class CanonicalizationFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="hspace"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformFlowNode(visitor=ProperOrder(), name="proper"),
        TransformFlowNode(visitor=PauliAlgebra(), name="paulialgebra"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath2"),
        TransformFlowNode(visitor=GatherPauli(), name="gatherpauli"),
        TransformFlowNode(visitor=NormalOrder(), name="normal"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute2"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath3"),
        TransformFlowNode(visitor=ProperOrder(), name="proper2"),
        TransformFlowNode(visitor=PruneIdentity(), name="prune"),
        TransformFlowNode(visitor=SortedOrder(), name="sorted"),
        TransformFlowNode(visitor=PartitionMathExpr(), name="partmath"),
        TransformFlowNode(visitor=DistributeMathExpr(), name="distmath"),
        TransformFlowNode(visitor=ProperOrderMathExpr(), name="propermath"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "hspace"

    def forward_hspace(self, model):
        self.namespace[self.current_node](model)
        self._current_node = "distribute"
        return model

    @FlowGraph.forward_factory
    def forward_distribute(self, model):
        return dict(done="gathermath")

    @FlowGraph.forward_factory
    def forward_gathermath(self, model):
        return dict(done="proper")

    @FlowGraph.forward_factory
    def forward_proper(self, model):
        return dict(done="paulialgebra")

    @FlowGraph.forward_factory
    def forward_paulialgebra(self, model):
        return dict(done="gathermath2")

    @FlowGraph.forward_factory
    def forward_gathermath2(self, model):
        return dict(done="gatherpauli")

    @FlowGraph.forward_factory
    def forward_gatherpauli(self, model):
        return dict(done="normal")

    @FlowGraph.forward_factory
    def forward_normal(self, model):
        return dict(done="sorted", repeat="distribute2")

    @FlowGraph.forward_factory
    def forward_distribute2(self, model):
        return dict(done="gathermath3")

    @FlowGraph.forward_factory
    def forward_gathermath3(self, model):
        return dict(done="proper2")

    @FlowGraph.forward_factory
    def forward_proper2(self, model):
        return dict(done="normal")

    @FlowGraph.forward_factory
    def forward_sorted(self, model):
        return dict(done="distmath")

    @FlowGraph.forward_factory
    def forward_distmath(self, model):
        return dict(done="propermath")

    @FlowGraph.forward_factory
    def forward_propermath(self, model):
        return dict(done="partmath")

    @FlowGraph.forward_factory
    def forward_partmath(self, model):
        return dict(done="terminal")


# ########################################################################################

if __name__ == "__main__":
    from rich import print as pprint
    from quantumion.interface.analog import *
    from quantumion.interface.math import *

    I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
    A, C, J = Annihilation(), Creation(), Identity()

    op = X @ C @ (X * Y) @ (A * C * C * A * C * C) @ (X @ X @ A @ C)
    fg = CanonicalizationFlow(name="g1", verbose=True)

    op = fg(op)
    pprint(op.accept(PrintOperator()))
