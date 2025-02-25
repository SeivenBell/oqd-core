from oqd_core.interface.analog.operator import *

# from oqd_core.interface.analog.operation import *
from rich import print as pprint

X = PauliX()
Y = PauliY()

pprint(X + Y + Y)
