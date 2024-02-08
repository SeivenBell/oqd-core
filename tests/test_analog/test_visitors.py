import numpy as np

########################################################################################

from quantumion.interface.analog import *
from quantumion.compiler.analog import AnalogCircuitIonsAnalysis

########################################################################################

if __name__ == "__main__":

    op = np.pi * PauliX @ PauliI @ PauliY
    gate = AnalogGate(duration=1 / 4, hamiltonian=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.evolve(gate=gate)

    acia = AnalogCircuitIonsAnalysis()

    ex.accept(acia)

    print(acia.ions)
