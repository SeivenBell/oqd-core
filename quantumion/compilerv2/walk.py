from abc import abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################
from rich import print as pprint

class Walk(PassBase):
    def __init__(self, rule: PassBase):
        super().__init__()

        self.rule = rule
        pass

    @abstractmethod
    def walk_VisitableBaseModel(self, model):
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        return self.walk(model)

    def walk(self, model):
        for cls in model.__class__.__mro__:
            map_func = getattr(self.rule, "map_{}".format(cls.__name__), None)
            if map_func:
                new_model = map_func(model)
                if new_model is not None:
                    return self.walk(new_model)
                """
                Notes:
                - this seems to be something like map children in liang
                - Understand class structure better now
                - [High Priority] show why it needs to be walk_VisitableBaseModel and not something like checkVisitableBaseModel function
                - This ensures graph traversal logic is handled by WALK and NOT rewrite rules
                - Understand why we don't need any maps inside due to this modification
                - how was is leaf case handled using previous method? i think we need another is leaf method to prevent unnecessary operations
                - One thing I don't understand is the repetiotion
                        walk model is class_='OperatorKron' op1=PauliI(class_='PauliI') op2=PauliY(class_='PauliY') and elems are (<class 
                        'quantumion.interface.analog.operator.OperatorKron'>, <class 'quantumion.interface.analog.operator.OperatorBinaryOp'>, <class 
                        'quantumion.interface.analog.operator.Operator'>, <class 'quantumion.interface.base.TypeReflectBaseModel'>, <class 
                        'quantumion.interface.base.VisitableBaseModel'>, <class 'pydantic.main.BaseModel'>, <class 'object'>)
                        walk map func is <bound method OperatorDistribute.map_OperatorKron of OperatorDistribute()>
                        *********************
                        new model is None
                        -------------------

                        walk model is OperatorKron and elems are (<class 'str'>, <class 'object'>)
                - current logic is that when return is None only then go to children as otherwise we won't be able to do lowering or return diff objects
                
                ## -----
                
                From CanVerPauliAlgebra
                    There is pattern matching involved. when we go to visit_Op, we go to the pattern Op and then the 
                    inner if statements try to do pattern matching
                    if no pattern matched for the given Op model which has been visited, we just return None
                ## -----
                """


        for cls in model.__class__.__mro__:
            walk_func = getattr(self, "walk_{}".format(cls.__name__), None)
            if walk_func:
                break

        if not walk_func:
            walk_func = self.generic_walk

        return walk_func(model)

    def generic_walk(self, model):
        return model

    pass


########################################################################################


class Pre(Walk):
    def walk_dict(self, model):
        return {k: self(v) for k, v in model.items()}

    def walk_list(self, model):
        return [self(e) for e in model]

    def walk_tuple(self, model):
        return tuple(self(e) for e in model)

    def walk_VisitableBaseModel(self, model):
        new_fields = {}
        for key in model.model_fields.keys():
            new_fields[key] = self(getattr(model, key))

        return model.__class__(**new_fields)


class Post(Walk):
    pass
