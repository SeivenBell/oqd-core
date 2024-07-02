from abc import ABC, abstractmethod

########################################################################################


class Walk(ABC):
    @abstractmethod
    def walk(self, rule):
        pass


########################################################################################


class Pre(Walk):
    def map(self, rule):
        pass


class Post(Walk):
    def map(self, rule):
        pass
