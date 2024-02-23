from typing import Any

from abc import ABC, abstractmethod, abstractproperty

########################################################################################

from quantumion.compiler.visitor import Visitor

########################################################################################


class FlowBase(ABC):
    def __init__(self, name, **kwargs):
        self.name = name
        pass

    @abstractproperty
    def namespace(self):
        pass

    pass


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
        return model

    pass


class TransformFlowNode(VisitorFlowNode):
    def __call__(self, model: Any):
        return model.accept(self.visitor)


class FlowGraph(FlowBase):
    def __init__(self, nodes, rootnode=None, max_iter=10, **kwargs):
        self.nodes = nodes
        self.max_iter = max_iter
        self._current_iter = 0

        if rootnode:
            if rootnode in self.namespace.keys():
                self.rootnode = rootnode
            raise NameError
        else:
            self.rootnode = self.nodes[0].name

        super().__init__(**kwargs)
        pass

    @property
    def namespace(self):
        _namespace = {self.name: self}
        for node in self.nodes:
            overlap = set(node.namespace.keys()) & set(_namespace.keys())
            if overlap:
                raise NameError("Overlapping Namespace: {}".format(",".join(overlap)))
            _namespace.update(node.namespace)
        return _namespace

    def __call__(self, model: Any):
        for node in self:
            model = node(model)
        return model

    def __iter__(self):
        self._current_iter = 0
        self._current_node = self.rootnode
        return self

    def __next__(self):
        self.exceeded_max_iter
        self._current_iter += 1
        return self.next()

    def next(self):
        print(self._current_node, end="->")
        return getattr(self, "next_{}".format(self._current_node))()

    @property
    def exceeded_max_iter(self):
        if self._current_iter >= self.max_iter:
            raise StopIteration
        pass

    pass


class CanonicalizationFlow(FlowGraph):
    def next_n1(self):
        def step(model: Any):
            model = self.namespace["n1"](model)
            self._current_node = "n2"
            return model

        return step

    def next_n2(self):
        def step(model: Any):
            model = self.namespace["n2"](model)
            self._current_node = "n1"
            return model

        return step

    def next_g1(self):
        def step(model: Any):
            model = self.namespace["g1"](model)
            self._current_node = "n3"
            return model

        return step

    def next_n3(self):
        def step(model: Any):
            model = self.namespace["n3"](model)
            self._current_node = "g1"
            return model

        return step


# ########################################################################################

if __name__ == "__main__":
    from quantumion.compiler.analog import *
    from quantumion.interface.analog import *

    I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
    A, C, J = Annihilation(), Creation(), Identity()

    vfn = TransformFlowNode(visitor=OperatorDistribute(), name="n1")
    vfn2 = TransformFlowNode(visitor=ProperOrder(), name="n2")
    vfn3 = TransformFlowNode(visitor=ProperOrder(), name="n3")

    fg = CanonicalizationFlow(nodes=(vfn, vfn2), name="g1")
    fg2 = CanonicalizationFlow(nodes=(fg, vfn3), name="g2")

    model = I * (X + X)
    model = fg2(model)
    print(model.accept(PrintOperator()))
