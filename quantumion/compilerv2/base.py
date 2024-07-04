from abc import ABC, abstractmethod

########################################################################################


class CompilerError(Exception):
    pass


class PassBase(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def children(self):
        pass

    def __call__(self, model):
        self._model = model

        try:
            model = self.map(model)
            if model is None:
                model = self._model
            return model
        except Exception as e:
            raise CompilerError(f"{e}")

    @abstractmethod
    def map(self, model):
        pass

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")
            ),
        )
