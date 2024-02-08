from typing import Any

########################################################################################

from quantumion.interfaces.base import VisitableBaseModel

########################################################################################


class Visitor:
    def visit(self, model: Any) -> Any:
        new_model = getattr(
            self, "visit_{}".format(model.__class__.__name__), self._visit
        )(model)
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


class Transform(Visitor):
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
    from quantumion.interfaces.base import TypeReflectBaseModel

    class A(TypeReflectBaseModel):
        value: int

    class B(TypeReflectBaseModel):
        value: int

    class C(TypeReflectBaseModel):
        a: A
        b: B

    class CTransform(Transform):
        def visit_A(self, model: A) -> A:
            assert isinstance(model, A)
            new_value = model.value + 1

            return A(value=new_value)

        def visit_B(self, model: B) -> B:
            assert isinstance(model, B)
            new_value = model.value * -1

            return B(value=new_value)

    model = C(a=A(value=1), b=B(value=2))

    Transform = Transform()
    ctransform = CTransform()

    new_model = model.accept(Transform)
    new_model2 = model.accept(ctransform)

    print(new_model)
    print(new_model2)
