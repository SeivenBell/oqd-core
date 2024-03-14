from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.operations import *

if __name__ == "__main__":
    from rich import print as pprint
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()