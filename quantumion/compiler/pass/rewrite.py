from abc import ABC, abstractmethod

########################################################################################

from quantumion.compiler.visitor import Visitor

########################################################################################


class Rewrite(ABC):
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def __call__(self, model):
        pass

    def process(self, rule):
        if isinstance(rule, Rewrite):
            return rule
        elif isinstance(rule, Visitor):
            return lambda model: rule.visit(model)

    pass


class Chain(Rewrite):
    def __init__(self, *rules):
        super().__init__()

        self.rules = rules
        pass

    def __call__(self, model):
        for rule in self.rules:
            model = self.process(rule)(model)

        return model


class FixedPoint(Rewrite):
    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    def __call__(self, model):

        current_iter = 0
        while True:
            _model = self.process(self.rule)(model)

            print(model, _model)
            if model == _model or current_iter > self.max_iter:
                model = _model
                break

            model = _model

        return model


########################################################################################

if __name__ == "__main__":

    class TestVisitor(Visitor):
        def visit_str(self, model: str):
            return "1"

    model = "hello world!"

    model = FixedPoint(TestVisitor())(model)

    print(model)
