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

    """
    say I have an extra input there whch is Operands. then for every model.operand, we first need to walk(model.operand) # not really rule(model.operand)
    as if u do that then u need to again write the logic for walking through lists
    """
class Operands():
    pass

class ConversionRule(RewriteRule):
    def __init__(self):
        super().__init__()
        self.target = QutipExperiment.model_fields

    def operands(self, model):
        # pprint("inside operands is {}".format(model))
        # new_model = {k: Pre(self)(v) for k, v in model.items()}
        new_model = PreWithNonVisitableOutput(self)(model)
        return new_model
        # if isinstance(model, list):
        #     return [self(elem) for elem in model]
        # else:
        #     return self(model)

    def map(self, model): # prolly need some operand here which will be first evaluated
        operands = None
        if isinstance(model, VisitableBaseModel):
            # pprint("map model is here:: {}\n".format(model))
            operands_dict = {}
            for key in model.model_fields.keys():
                operands_dict[key] = getattr(model, key)
            # pprint("\n exp is {}\n model is {}\n ".format(operands_dict, model))
            operands = self.operands(operands_dict)

        for cls in model.__class__.__mro__:
            map_func = getattr(self, "map_{}".format(cls.__name__), None)
            if map_func:
                break


        if not map_func:
            map_func = self.generic_map

        

        return map_func(model, operands)
    
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
