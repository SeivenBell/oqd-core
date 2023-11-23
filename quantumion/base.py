from typing import Optional
from pydantic import BaseModel, model_validator

########################################################################################


class TypeReflectBaseModel(BaseModel):
    type_: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def reflect(cls, data):
        if "type_" in data.keys():
            if data["type_"] != cls.__name__:
                raise TypeReflectError(
                    'discrepency between "type_" field and model type'
                )

        data["type_"] = cls.__name__
        return data


class TypeReflectError(Exception):
    pass
