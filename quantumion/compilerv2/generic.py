from abc import abstractmethod
from quantumion.compilerv2.base import PassBase

########################################################################################


class GenericRewriter(PassBase):

    def map(self, model):
        return self.rewriter(model)


########################################################################################


class Chain(GenericRewriter):
    def __init__(self, *rules):
        super().__init__()

        self.rules = list(rules)
        pass

    @property
    def children(self):
        return self.rules

    def map(self, model):
        for rule in self.rules:
            new_model = rule(model)
        return new_model


class FixedPoint(GenericRewriter):
    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        i = 0
        new_model = model
        while True:
            _model = self.rule(new_model)

            if _model == new_model or i >= self.max_iter:
                return new_model

            new_model = _model
            i += 1


class Single(GenericRewriter):
    def __init__(self, rule):
        super().__init__()

        self.rule = rule
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        new_model = self.rule(model)
        return new_model
