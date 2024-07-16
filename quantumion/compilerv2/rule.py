from quantumion.compilerv2.base import PassBase

########################################################################################

from rich import print as pprint
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
            map_func = self.generic_map

        return map_func(model)

    def generic_map(self, model):
        return model

    # def map(self, model):
    #     for cls in model.__class__.__mro__:
    #         map_func = getattr(self, "map_{}".format(cls.__name__), None)
    #         if map_func:
    #             map_func(model)
    #             break
    pass


########################################################################################


class PrintCurrent(RewriteRule):
    def __init__(self, *, print_fn=print):
        super().__init__()

        self.print_fn = print_fn
        self.current = 0
        pass

    def generic_map(self, model):
        self.print_fn(f"{self.current}: {model.__class__.__name__}({model})")
        self.current += 1
        pass


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

    def map_int(self, model):
        return model + self.N

    def map_str(self, model):
        return str(int(model) + self.N)
