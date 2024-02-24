from typing import Any, List, Optional, Union

from abc import ABC, abstractmethod, abstractproperty

from quantumion.interface.base import TypeReflectBaseModel

########################################################################################

from quantumion.compiler.visitor import Visitor
from quantumion.compiler.analog import *
from quantumion.compiler.math import *

########################################################################################


class TraversalSite(TypeReflectBaseModel):
    iteration: str
    node: str
    subtraversal: Optional["Traversal"] = None
    emission: Any = None


class Traversal(TypeReflectBaseModel):
    sites: List[TraversalSite] = []

    class Config:
        validate_assignment = True


########################################################################################


class ForwardDecorators:
    @staticmethod
    def forward_once(method):
        def _method(self, model: Any) -> FlowOut:
            flowout = self.namespace[self.current_node](model)

            instructions = method(self, model)
            self.next_node = instructions["done"]

            return flowout

        return _method

    @staticmethod
    def forward_fixed_point(method):
        def _method(self, model: Any) -> FlowOut:
            flowout = self.namespace[self.current_node](model)

            instructions = method(self, model)

            if model == flowout.model:
                self.next_node = instructions["done"]

            return flowout

        return _method

    @staticmethod
    def forward_return(method):
        def _method(self, model: Any) -> FlowOut:
            flowout = self.namespace[self.current_node](model)

            instructions = method(self, model)

            if model == flowout.model:
                self.next_node = instructions["done"]
            elif "return" in instructions.keys():
                self.next_node = instructions["return"]

            return flowout

        return _method


########################################################################################


class FlowBase(ABC):
    def __init__(self, name, **kwargs):
        self.name = name
        pass

    @abstractmethod
    def __call__(self, model: Any) -> "FlowOut":
        pass

    @abstractproperty
    def traversal(self) -> Union[Traversal, None]:
        pass

    pass


class FlowOut(TypeReflectBaseModel):
    model: Any
    emission: Any = None


########################################################################################


class FlowNode(FlowBase):
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, model: Any) -> FlowOut:
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

    def __call__(self, model: Any) -> FlowOut:
        model.accept(self.visitor)
        return FlowOut(model=model)

    pass


class TransformFlowNode(VisitorFlowNode):
    def __call__(self, model: Any) -> FlowOut:
        return FlowOut(model=model.accept(self.visitor))


########################################################################################


class FlowGraph(FlowBase):
    nodes: List[FlowBase] = [FlowTerminal(name="terminal")]
    rootnode: str = ""

    @property
    def namespace(self):
        _namespace = {}
        overlap = set()
        for node in self.nodes:
            if node.name in _namespace.keys():
                overlap.add(node.name)
            _namespace[node.name] = node

        if overlap:
            raise NameError(
                "Multiple nodes with names: {}".format(
                    ", ".join({f'"{name}"' for name in overlap})
                )
            )

        return _namespace

    def __init__(self, max_iter=1000, **kwargs):
        self.max_iter = max_iter

        super().__init__(**kwargs)
        pass

    @property
    def exceeded_max_iter(self):
        if self.current_iter >= self.max_iter:
            raise RecursionError(f"Exceeded number of iterations allowed for {self}")
        pass

    @property
    def current_node(self):
        return self._current_node

    @current_node.setter
    def current_node(self, value):
        if value in self.namespace.keys():
            self._current_node = value
            return
        raise NameError(f'No node named "{value}" in namespace of {self}')

    @property
    def next_node(self):
        return self._next_node

    @next_node.setter
    def next_node(self, value):
        if value in self.namespace.keys():
            self._next_node = value
            return
        raise NameError(f'No node named "{value}" in namespace of {self}')

    @property
    def current_iter(self):
        return self._current_iter

    @property
    def traversal(self) -> Traversal:
        return self._traversal

    def __iter__(self):
        self.current_node = self.rootnode
        self._current_iter = 0
        self._traversal = Traversal()
        return self

    def __next__(self):
        self.exceeded_max_iter

        if isinstance(self.namespace[self.current_node], FlowTerminal):
            self._traversal.sites += [
                TraversalSite(
                    iteration=str(self.current_iter),
                    node=self.current_node,
                ),
            ]
            raise StopIteration

        def _forward(model: Any):
            flowout = getattr(self, "forward_{}".format(self.current_node))(model)

            self._traversal.sites += [
                TraversalSite(
                    iteration=str(self.current_iter),
                    node=self.current_node,
                    subtraversal=self.namespace[self.current_node].traversal,
                    emission=flowout.emission,
                ),
            ]

            self.current_node = self.next_node

            self._current_iter += 1
            return flowout.model

        return _forward

    def __call__(self, model) -> FlowOut:
        for node in self:
            model = node(model)
        return FlowOut(model=model)


########################################################################################


class NormalOrderFlow(FlowGraph):
    nodes = [
        TransformFlowNode(visitor=NormalOrder(), name="normal"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformFlowNode(visitor=ProperOrder(), name="proper"),
        TransformFlowNode(visitor=PruneIdentity(), name="prune"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "normal"

    @ForwardDecorators.forward_once
    def forward_normal(self, model):
        return dict(done="distribute")

    @ForwardDecorators.forward_fixed_point
    def forward_distribute(self, model):
        return dict(done="gathermath")

    @ForwardDecorators.forward_fixed_point
    def forward_gathermath(self, model):
        return dict(done="proper")

    @ForwardDecorators.forward_fixed_point
    def forward_proper(self, model):
        return dict(done="prune")

    @ForwardDecorators.forward_fixed_point
    def forward_prune(self, model):
        return dict(done="terminal")


class CanonicalizationFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="hspace"),
        TransformFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformFlowNode(visitor=ProperOrder(), name="proper"),
        TransformFlowNode(visitor=PauliAlgebra(), name="paulialgebra"),
        TransformFlowNode(visitor=GatherMathExpr(), name="gathermath2"),
        TransformFlowNode(visitor=GatherPauli(), name="gatherpauli"),
        NormalOrderFlow(name="normalflow"),
        TransformFlowNode(visitor=SortedOrder(), name="sorted"),
        TransformFlowNode(visitor=DistributeMathExpr(), name="distmath"),
        TransformFlowNode(visitor=ProperOrderMathExpr(), name="propermath"),
        TransformFlowNode(visitor=PartitionMathExpr(), name="partmath"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "hspace"

    @ForwardDecorators.forward_once
    def forward_hspace(self, model):
        return dict(done="distribute")

    @ForwardDecorators.forward_fixed_point
    def forward_distribute(self, model):
        return dict(done="gathermath")

    @ForwardDecorators.forward_fixed_point
    def forward_gathermath(self, model):
        return dict(done="proper")

    @ForwardDecorators.forward_fixed_point
    def forward_proper(self, model):
        return dict(done="paulialgebra")

    @ForwardDecorators.forward_fixed_point
    def forward_paulialgebra(self, model):
        return dict(done="gathermath2")

    @ForwardDecorators.forward_fixed_point
    def forward_gathermath2(self, model):
        return dict(done="gatherpauli")

    @ForwardDecorators.forward_fixed_point
    def forward_gatherpauli(self, model):
        return dict(done="normalflow")

    @ForwardDecorators.forward_fixed_point
    def forward_normalflow(self, model):
        return dict(done="sorted")

    @ForwardDecorators.forward_fixed_point
    def forward_sorted(self, model):
        return dict(done="distmath")

    @ForwardDecorators.forward_fixed_point
    def forward_distmath(self, model):
        return dict(done="propermath")

    @ForwardDecorators.forward_fixed_point
    def forward_propermath(self, model):
        return dict(done="partmath")

    @ForwardDecorators.forward_fixed_point
    def forward_partmath(self, model):
        return dict(done="terminal")


# ########################################################################################

if __name__ == "__main__":
    from rich import print as pprint
    from quantumion.interface.analog import *
    from quantumion.interface.math import *

    I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
    A, C, J = Annihilation(), Creation(), Identity()

    op = X @ (A * C)
    fg = CanonicalizationFlow(name="g1")

    op = fg(op).model
    pprint(op.accept(PrintOperator()))

    pprint(fg.traversal)
