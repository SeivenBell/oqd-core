from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, model_validator

########################################################################################


class BackendBase(ABC):
    @abstractmethod
    def run(self, task):
        pass

    pass


########################################################################################


class TypeReflectBaseModel(BaseModel):
    class_: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def reflect(cls, data):
        if "class_" in data.keys():
            if data["class_"] != cls.__name__:
                raise TypeReflectError(
                    'discrepency between "class_" field and model type'
                )

        data["class_"] = cls.__name__
        return data


class TypeReflectError(Exception):
    pass
