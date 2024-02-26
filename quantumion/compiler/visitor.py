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

        if isinstance(model, VisitableBaseModel):
            new_fields = {}
            for key in model.model_fields.keys():
                new_fields[key] = self.visit(model.__dict__[key])
            new_model = model.__class__(**new_fields)

        return new_model


if __name__ == "__main__":
    from quantumion.interface.base import TypeReflectBaseModel

    class A(TypeReflectBaseModel):
        value: int

    class B(TypeReflectBaseModel):
        value: int

    class C(TypeReflectBaseModel):
        a: A
        b: B

    class CTransformer(Transformer):
        def visit_A(self, model: A) -> A:
            assert isinstance(model, A)
            new_value = model.value + 1

            return A(value=new_value)

        def visit_B(self, model: B) -> B:
            assert isinstance(model, B)
            new_value = model.value * -1

            return B(value=new_value)

    model = C(a=A(value=1), b=B(value=2))

    Transformer = Transformer()
    ctransformer = CTransformer()

    new_model = model.accept(Transformer)
    new_model2 = model.accept(ctransformer)

    print(new_model)
    print(new_model2)
