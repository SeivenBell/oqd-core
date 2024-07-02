from abc import ABC, abstractmethod

########################################################################################


class CompilerError(Exception):
    pass


class PassBase(ABC):
    def __call__(self, model):
        self.model = model

        try:
            model = self.map(model)
            if model is None:
                model = self.model
            return model
        except Exception as e:
            raise CompilerError(f"{e}")

    @abstractmethod
    def map(self, model):
        pass

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ",".join(f"{k}={v}" for k, v in self.__dict__.items() if k != "model"),
        )
