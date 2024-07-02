from abc import abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class Walk(PassBase):
    def __init__(self, rule: PassBase):
        self.rule = rule

    @abstractmethod
    def walk(self):
        pass

    def map(self, model):
        return self.walk()(model)

    pass


########################################################################################


class Pre(Walk):
    def walk(self):
        def map(model):
            if isinstance(model, dict):
                new_model = {k: self.rule(v) for k, v in model.items()}
            elif isinstance(model, list):
                new_model = [self.rule(e) for e in model]
            else:
                new_model = self.rule(model)

            return new_model

        return map


class Post(Walk):
    def walk(self):
        pass
