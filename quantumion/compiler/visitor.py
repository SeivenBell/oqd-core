from typing import Any

########################################################################################

from quantumion.interface.base import VisitableBaseModel

########################################################################################


class Visitor:
    def visit(self, model: Any) -> Any:
        for cls in model.__class__.__mro__:
            visit_func = getattr(self, "visit_{}".format(cls.__name__), None)
            if visit_func:
                break

        if not visit_func:
            visit_func = self._visit

        new_model = visit_func(model)
        return new_model

    def _visit(self, model: Any) -> Any:
        if isinstance(
            model,
            (list,),
        ):
            [self.visit(element) for element in model]

        if isinstance(model, dict):
            for key, value in model.items():
                if isinstance(key, VisitableBaseModel):
                    self.visit(key)
                
                if isinstance(value, VisitableBaseModel):
                    self.visit(value)

        if isinstance(model, VisitableBaseModel):
            new_fields = {}
            for key in model.model_fields.keys():
                new_fields[key] = self.visit(model.__dict__[key])

    def reset(self):
        pass

    def emit(self, model: Any):
        model.accept(self)
        return


class Transformer(Visitor):
    def _visit(self, model: Any) -> Any:
        new_model = model

        if isinstance(
            model,
            (list,),
        ):
            new_model = model.__class__([self.visit(element) for element in model])

        elif isinstance(model, dict):
            new_model = {}
            for key, value in model.items():
                if isinstance(key, VisitableBaseModel):
                    key = self.visit(key)
                
                if isinstance(value, VisitableBaseModel):
                    value = self.visit(value)
                    
                new_model[key] = value

        if isinstance(model, VisitableBaseModel):
            new_fields = {}
            for key in model.model_fields.keys():
                new_fields[key] = self.visit(model.__dict__[key])
            new_model = model.__class__(**new_fields)

        return new_model
