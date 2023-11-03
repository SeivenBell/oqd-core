# External exports

from abc import ABC, abstractmethod

from pydantic import BaseModel

########################################################################################


class BackendBase(ABC):
    @abstractmethod
    def run(self, task):
        pass

    pass
