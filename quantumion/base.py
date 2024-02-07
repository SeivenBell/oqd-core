from typing import Optional
from pydantic import BaseModel, model_validator

from quantumion.compiler.visitor import Visitor

########################################################################################


class VisitableBaseModel(BaseModel):
    def accept(self, visitor: Visitor):
        visitor.reset()
        return visitor.visit(self)


class TypeReflectBaseModel(VisitableBaseModel):
    class_: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def reflect(cls, data):
        if isinstance(data, BaseModel):
            return data
        if "class_" in data.keys():
            if data["class_"] != cls.__name__:
                raise ValueError('discrepency between "class_" field and model type')

        data["class_"] = cls.__name__

        return data
