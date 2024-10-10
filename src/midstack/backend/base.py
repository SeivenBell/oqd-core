from abc import ABC, abstractmethod

########################################################################################


class BackendBase(ABC):
    @abstractmethod
    def run(self, task):
        pass

    pass
