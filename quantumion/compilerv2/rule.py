from abc import ABC, abstractmethod

########################################################################################


class RewriteRule(ABC):
    @abstractmethod
    def map(self, node):
        pass


########################################################################################
