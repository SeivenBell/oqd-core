from abc import abstractmethod
from quantumion.compilerv2.base import PassBase

########################################################################################


class GenericRewriter(PassBase):
    @abstractmethod
    def logic(self):
        pass

    def map(self, model):
        return self.logic()(model)


########################################################################################


class Chain(GenericRewriter):
    def __init__(self, *rules):
        super().__init__()

        self.rules = list(rules)
        pass

    def logic(self):
        def map(model):
            for rule in self.rules:
                model = rule(model)
            return model

        return map

        pass


class FixedPoint(GenericRewriter):
    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    def logic(self):
        def map(model):
            i = 0
            while True:
                _model = self.rule(model)

                if _model == model or i >= self.max_iter:
                    return model

                model = _model
                i += 1

        return map


class Single(GenericRewriter):
    def __init__(self, rule):
        super().__init__()

        self.rule = rule
        pass

    def logic(self):
        def map(model):
            model = self.rule(model)
            return model

        return map
