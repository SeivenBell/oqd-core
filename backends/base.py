from abc import abstractmethod
from pydantic import BaseModel


class BackendBase(BaseModel):
    @abstractmethod
    def run(self, task):
        pass

    pass
