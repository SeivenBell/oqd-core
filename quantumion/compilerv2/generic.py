from abc import ABC, abstractmethod

########################################################################################


class GenericRewriter(ABC):
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def map(self):
        pass

    pass


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
