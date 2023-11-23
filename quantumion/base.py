from typing import Optional
from pydantic import BaseModel, model_validator


class TypeReflectBaseModel(BaseModel):
    class_: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def reflect(cls, data):
        if "class_" in data.keys():
            if data["class_"] != cls.__name__:
                raise TypeReflectError(
                    f'"class_" field {data["class_"]} and model type {cls.__name__} do not match.'
                )

        data["class_"] = cls.__name__
        return data


class TypeReflectError(Exception):
    pass
