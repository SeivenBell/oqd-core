from quantumion.compilerv2.base import PassBase

########################################################################################


class RewriteRule(PassBase):
    def map(self, model):
        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break

        if not map_func:
            map_func = self.generic_map

        new_model = map_func(model)
        return new_model

    def generic_map(self, model):
        return model

    pass


########################################################################################


class AddOne(RewriteRule):
    def generic_map(self, model):
        from numbers import Number

        if isinstance(model, Number):
            return model + 1
        else:
            return None

    def map_str(self, model):
        return str(int(model) + 1)


class AddN(RewriteRule):
    def __init__(self, N):
        super().__init__()

        self.N = N
        pass

    def generic_map(self, model):
        from numbers import Number

        if isinstance(model, Number):
            return model + self.N
        else:
            return None

    def map_str(self, model):
        return str(int(model) + self.N)
