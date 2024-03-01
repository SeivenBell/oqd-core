from typing import List, Any

########################################################################################

from quantumion.compiler.math import *
from quantumion.compiler.analog import *
from quantumion.compiler.flow.base import *
from quantumion.compiler.flow.flowout import *
from quantumion.compiler.flow.flownode import *
from quantumion.compiler.flow.traversal import *
from quantumion.compiler.flow.forward_decorators import *

########################################################################################

__all__ = [
    "FlowGraph",
    "VerificationFlowGraphCreator",
    "NormalOrderFlow",
    "CanonicalizationFlow",
]


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

    def __init__(self, max_steps=1000, **kwargs):
        self.max_steps = max_steps

        if FlowTerminal not in [node.__class__ for node in self.nodes]:
            raise FlowError("FlowGraph does not contain a terminal node")

        super().__init__(**kwargs)
        pass

    @property
    def exceeded_max_steps(self):
        if self.current_step >= self.max_steps:
            raise RecursionError(f"Exceeded number of steps allowed for {self}")
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

    @next_node.deleter
    def next_node(self):
        del self._next_node
        pass

    @property
    def current_step(self):
        return self._current_step

    @property
    def traversal(self) -> Traversal:
        return self._traversal

    def __iter__(self):
        self.current_node = self.rootnode
        self._current_step = 0
        self._traversal = Traversal()
        return self

    def __next__(self):
        self.exceeded_max_steps

        if isinstance(self.namespace[self.current_node], FlowTerminal):
            self._traversal.sites += [
                TraversalSite(
                    site=str(self.current_step),
                    node=self.current_node,
                ),
            ]
            raise StopIteration

        def _forward(model: Any):
            flowout = getattr(self, "forward_{}".format(self.current_node))(model)

            self._traversal.sites += [
                TraversalSite(
                    site=str(self.current_step),
                    node=self.current_node,
                    subtraversal=self.namespace[self.current_node].traversal,
                    emission=flowout.emission,
                    model=flowout.model,
                ),
            ]

            self.current_node = self.next_node
            self._current_step += 1

            del self.next_node

            return flowout.model

        return _forward

    def __call__(self, model: Any, traversal: Traversal = Traversal()) -> FlowOut:
        for forward in self:
            model = forward(model)
        return FlowOut(model=model)


########################################################################################


def VerificationFlowGraphCreator(verify, transformer):
    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_error(redirect="transformer")
    @forward_decorators.forward_once(done="terminal")
    def forward_verify(self, model):
        pass

    @forward_decorators.forward_return()
    def forward_transformer(self, model):
        pass

    return type(
        "VerificationFlowGraph",
        (FlowGraph,),
        dict(
            nodes=[
                VisitorFlowNode(visitor=verify, name="verify"),
                TransformerFlowNode(visitor=transformer, name="transformer"),
                FlowTerminal(name="terminal"),
            ],
            rootnode="verify",
            forward_decorators=forward_decorators,
            forward_verify=forward_verify,
            forward_transformer=forward_transformer,
        ),
    )


########################################################################################


class MathCanonicalizationFlow(FlowGraph):
    nodes = [
        FlowTerminal(name="terminal"),
        TransformerFlowNode(visitor=DistributeMathExpr(), name="distribute"),
        TransformerFlowNode(visitor=ProperOrderMathExpr(), name="proper"),
        TransformerFlowNode(visitor=PartitionMathExpr(), name="partition"),
    ]
    rootnode = "distribute"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_fixed_point(done="proper")
    def forward_distribute(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="partition")
    def forward_proper(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="terminal")
    def forward_partition(self, model):
        pass

    pass


########################################################################################


class NormalOrderFlow(FlowGraph):
    nodes = [
        TransformerFlowNode(visitor=NormalOrder(), name="normal"),
        TransformerFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformerFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformerFlowNode(visitor=ProperOrder(), name="proper"),
        TransformerFlowNode(visitor=PruneIdentity(), name="prune"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "normal"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_once(done="distribute")
    def forward_normal(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="gathermath")
    def forward_distribute(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="proper")
    def forward_gathermath(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="prune")
    def forward_proper(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="terminal")
    def forward_prune(self, model):
        pass


########################################################################################


class CanonicalizationFlow(FlowGraph):
    nodes = [
        FlowTerminal(name="terminal"),
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="hspace"),
        TransformerFlowNode(visitor=GatherMathExpr(), name="gathermath"),
        TransformerFlowNode(visitor=OperatorDistribute(), name="distribute"),
        TransformerFlowNode(visitor=ProperOrder(), name="proper"),
        TransformerFlowNode(visitor=PauliAlgebra(), name="paulialgebra"),
        TransformerFlowNode(visitor=GatherMathExpr(), name="gathermath2"),
        TransformerFlowNode(visitor=GatherPauli(), name="gatherpauli"),
        NormalOrderFlow(name="normalorder"),
        TransformerFlowNode(visitor=SortedOrder(), name="sorted"),
        MathCanonicalizationFlow(name="mathcanonicalization"),
    ]
    rootnode = "hspace"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_once(done="gathermath")
    def forward_hspace(self, model):
        pass

    @forward_decorators.forward_detour(done="proper", detour="distribute")
    def forward_gathermath(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="gathermath")
    def forward_distribute(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="paulialgebra")
    def forward_proper(self, model):
        pass

    @forward_decorators.forward_detour(done="gatherpauli", detour="gathermath2")
    def forward_paulialgebra(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="paulialgebra")
    def forward_gathermath2(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="normalorder")
    def forward_gatherpauli(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="sorted")
    def forward_normalorder(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="mathcanonicalization")
    def forward_sorted(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="terminal")
    def forward_mathcanonicalization(self, model):
        pass
