from quantumion.compilerv2.base import PassBase
from quantumion.interface.base import VisitableBaseModel

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
            map_func = self.generic_map

        return map_func(model)

    def generic_map(self, model):
        return model

    pass


class ConversionRule(RewriteRule):
    def __init__(self):
        super().__init__()

        self.operands = None


########################################################################################


class PrettyPrint(ConversionRule):
    def __init__(self, *, indent="  "):
        super().__init__()

        self.indent = indent

    def generic_map(self, model):
        return f"{model.__class__.__name__}({model})"

    def map_list(self, model):
        s = f"{model.__class__.__name__}"

        print(self.operands)
        _s = ""
        for n, o in enumerate(self.operands):
            _s += f"\n{self.indent}- {n}: " + f"\n{self.indent}".join(o.split("\n"))

        s = s + _s

        return s

    def map_tuple(self, model):
        s = f"{model.__class__.__name__}"

        _s = ""
        for n, o in enumerate(self.operands):
            _s += f"\n{self.indent}- {n}: " + f"\n{self.indent}".join(o.split("\n"))

        s = s + _s

        return s

    def map_dict(self, model):
        s = f"{model.__class__.__name__}"

        _s = ""
        for k, v in self.operands.items():
            _s += f"\n{self.indent}- {k}: " + f"\n{self.indent}".join(v.split("\n"))

        s = s + _s

        return s

    def map_VisitableBaseModel(self, model):
        s = f"{model.__class__.__name__}"

        _s = ""
        for k, v in self.operands.items():
            _s += f"\n{self.indent}- {k}: " + f"\n{self.indent}".join(v.split("\n"))

        s = s + _s

        return s
