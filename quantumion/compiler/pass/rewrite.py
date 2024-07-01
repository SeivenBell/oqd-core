from abc import ABC, abstractmethod

########################################################################################

from quantumion.compiler.visitor import Visitor

########################################################################################


class GenericRewriter(ABC):
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def __call__(self, model):
        pass

    def map(self, rule):
        if isinstance(rule, GenericRewriter):
            return rule
        elif isinstance(rule, Visitor):
            return lambda model: rule.visit(model)

    pass


class Chain(GenericRewriter):
    def __init__(self, *rules):
        super().__init__()

        self.rules = rules
        pass

    def __call__(self, model):
        for rule in self.rules:
            model = self.map(rule)(model)

        return model


class FixedPoint(GenericRewriter):
    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    def __call__(self, model):

        current_iter = 0
        while True:
            _model = self.map(self.rule)(model)

            print(model, _model)
            if model == _model or current_iter > self.max_iter:
                model = _model
                break

            model = _model

        return model


class Single(GenericRewriter):
    def __init__(self, rule):
        super().__init__()

        self.rule = rule
        pass

    def __call__(self, model):
        model = self.map(self.rule)(model)

        return model


########################################################################################

if __name__ == "__main__":

    class TestVisitor(Visitor):
        def visit_str(self, model: str):
            return "1"

    model = "hello world!"

    model = FixedPoint(TestVisitor())(model)

    print(model)
