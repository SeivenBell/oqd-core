from abc import abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class Walk(PassBase):
    def __init__(self, rule: PassBase):
        self.rule = rule

    @abstractmethod
    def walk(self):
        pass

    def map(self, model):
        return self.walk()(model)

    pass


########################################################################################


class Pre(Walk):
    def walk(self):
        pass


class Post(Walk):
    def walk(self):
        pass
