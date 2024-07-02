from abc import ABC, abstractmethod

########################################################################################

from quantumion.compilerv2.base import PassBase

########################################################################################


class RewriteRule(PassBase):
    pass


########################################################################################


class AddOne(RewriteRule):
    def map(self, model):
        from numbers import Number

        if isinstance(model, Number):
            return model + 1
        else:
            raise TypeError("Incompatible input type for AddOne")
