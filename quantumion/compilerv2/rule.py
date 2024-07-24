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


########################################################################################


class PrettyPrint(RewriteRule):
    def __init__(self):
        super().__init__()

        self.operands = []

    def generic_map(self, model):
        s = f"{model.__class__.__name__}"

        _s = ""
        if isinstance(model, list):
            for i, _ in enumerate(model):
                _s = (
                    f"\n  {len(model) - i}: "
                    + "\n  ".join(self.operands.pop().split("\n"))
                    + _s
                )
        elif isinstance(model, VisitableBaseModel):
            for k in reversed(model.model_fields.keys()):
                if k == "class_":
                    continue
                _s = f"\n  {k}: " + "\n  ".join(self.operands.pop().split("\n")) + _s
        else:
            _s = f"({model})"

        self.operands.append(s + _s)
        return model
