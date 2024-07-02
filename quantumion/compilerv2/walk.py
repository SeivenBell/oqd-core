from abc import abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class Walk(PassBase):
    def __init__(self, rule: PassBase):
        super().__init__()

        self.rule = rule
        pass

    def map(self, model):
        return self.walk(model)

    def walk(self, model):
        for cls in model.__class__.__mro__:
            walk_func = getattr(self, "walk_{}".format(cls.__name__), None)
            if walk_func:
                break

        if not walk_func:
            walk_func = self.generic_walk

        new_model = walk_func(model)
        return new_model

    def generic_walk(self, model):
        return self.rule(model)

    pass


########################################################################################


class Pre(Walk):
    def walk_dict(self, model):
        return {k: self(v) for k, v in model.items()}

    def walk_list(self, model):
        return [self(e) for e in model]

    def walk_tuple(self, model):
        return tuple(self(e) for e in model)


class Post(Walk):
    pass
