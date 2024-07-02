from abc import ABC, abstractmethod

########################################################################################


class PassBase(ABC):
    def __call__(self, model):
        return self.map(model)

    @abstractmethod
    def map(self, model):
        pass
