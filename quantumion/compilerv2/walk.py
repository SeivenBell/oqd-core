from abc import abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class Walk(PassBase):
    def __init__(self, rule: PassBase, branches=(list, dict, tuple)):
        super().__init__()

        self.rule = rule
        self._branches = tuple(branches)
        pass

    @abstractmethod
    def walk(self):
        pass

    def map(self, model):
        return self.walk()(model)

    def is_branch(self, model):
        if isinstance(model, (self._branches)):
            return True
        else:
            return False


########################################################################################


class Pre(Walk):
    def walk(self):
        def map(model):
            if self.is_branch(model):
                if isinstance(model, dict):
                    new_model = {k: self(v) for k, v in model.items()}
                elif isinstance(model, (list, tuple)):
                    new_model = model.__class__([self(e) for e in model])
                else:
                    new_model = self(model)
            else:
                new_model = self.rule(model)

            return new_model

        return map


class Post(Walk):
    def walk(self):
        pass
