from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.operations import *
from rich import print as pprint

__all__ = [
    "QutipBackendTransformer",
]
class QutipCompiler(AnalogInterfaceTransformer):
    """Transformer to run an experiment (maybe use visitor?)"""

class QutipBackendTransformer(AnalogInterfaceTransformer):
    """convert task to QutipObj without running (maybe use visitor?)"""

    def visit_Evolve(self, model: Evolve):
        pprint("Model is {}".format(model))
        return model

if __name__ == "__main__":
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()