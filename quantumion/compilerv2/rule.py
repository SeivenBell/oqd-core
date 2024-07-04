import inspect

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class RewriteRule(PassBase):
    @property
    def children(self):
        return []

    def map(self, model):
        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break

        if not map_func:
            raise TypeError(
                f"Rule {self.__class__.__name__} does not apply to model of type {model.__class__.__name__}"
            )

        new_model = map_func(model)
        return new_model

    pass


########################################################################################


class AddOne(RewriteRule):
    def map_int(self, model):
        return model + 1

    def map_str(self, model):
        return str(int(model) + 1)


class AddN(RewriteRule):
    def __init__(self, N):
        super().__init__()

        self.N = N
        pass

    def map_str(self, model):
        return str(int(model) + self.N)
