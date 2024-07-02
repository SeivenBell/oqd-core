from abc import abstractmethod
from quantumion.compilerv2 import PassBase

########################################################################################


class GenericRewriter(PassBase):
    @abstractmethod
    def compose(self):
        pass

    def map(self, model):
        return self.compose()(model)


########################################################################################


class Chain(GenericRewriter):
    def __init__(self, *rules):
        super().__init__()

        self.rules = rules
        pass


class FixedPoint(GenericRewriter):
    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass


class Single(GenericRewriter):
    def __init__(self, rule):
        super().__init__()

        self.rule = rule
        pass
