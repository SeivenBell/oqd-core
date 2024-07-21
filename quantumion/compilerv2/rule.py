from quantumion.compilerv2.base import PassBase
from quantumion.interface.base import VisitableBaseModel

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

    # For verfications this is enough
    # def map(self, model):
    #     for cls in model.__class__.__mro__:
    #         map_func = getattr(self, "map_{}".format(cls.__name__), None)
    #         if map_func:
    #             map_func(model)
    #             break
    pass

class ConversionRule(RewriteRule):
    def __init__(self, operands = None):
        super().__init__()
        self.operands = None

    def map(self, model): # prolly need some operand here which will be first evaluated
        operands = self.operands if isinstance(model, VisitableBaseModel) else None
        # operands = self.operands
        # pprint("in map the operands is {} and model is {}".format(operands, model))
        """
        Commented out logic is now part of ConversionWalk
        """
        # if isinstance(model, VisitableBaseModel):
        #     # pprint("map model is here:: {}\n".format(model))
        #     operands_dict = {}
        #     for key in model.model_fields.keys():
        #         operands_dict[key] = getattr(model, key)
        #     pprint("\n exp is {}\n model is {}\n ".format(operands_dict, model))
        #     operands = self.operands(operands_dict)

        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break

        if not map_func:
            map_func = self.generic_map

        return map_func(model, operands = operands)

    def generic_map(self, model, operands):
        return model
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
