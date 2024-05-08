from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.interface.analog.operations import *
from quantumion.interface.analog.operator import *
from quantumion.interface.atomic import *
import numpy as np
from rich import print as pprint

class AnalogIRtoAtomicIR(AnalogInterfaceTransformer):

    def __init__(self) -> None:
        super().__init__()
        self.delta = 2 * (6.626*(10**(-34))) * np.pi * (3*(10**8)) * ((1/(355*(10**(-9)))) - (1/(369*(10**(-9)))))
        self.phi = 2

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        return self.visit(model.sequence)
    
    def visit_Evolve(self, model: Evolve):
        omega  = self.visit(model.gate.hamiltonian)
        omega_A = (omega*2*self.delta)**(1/2)
        omega_B = omega_A
        phi_A = self.phi
        phi_B = -self.phi
        level = Level(energy = 100)
        transition = Transition(
            level1 = level,
            level2 = level,
            einsteinA=1.0
        )
        beam_A = Beam(
            transition=transition,
            rabi=omega_A,
            detuning=self.delta,
            phase=phi_A,
            polarization=[-1,1],
            wavevector=[0,0,1],
            target=0
        )

        beam_B = Beam(
            transition=transition,
            rabi=omega_B,
            detuning=self.delta,
            phase=phi_B,
            polarization=[-1,1],
            wavevector=[0,0,1],
            target=0
        )

        pulse_A = Pulse(
            beam = beam_A,
            duration = model.duration
        )
        pulse_B = Pulse(
            beam = beam_B,
            duration = model.duration
        )

        protocol = SequentialProtocol(sequence = [pulse_A, pulse_B])
        return protocol

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if not isinstance(model.op, (PauliX, PauliY)):
            raise Exception("Unsupported operation")
        return (model.expr**2)**(1/2)

    def visit_OperatorAdd(self, model: OperatorAdd):
        if not isinstance(model.op1.op, (PauliX, PauliY)) or not isinstance(model.op2.op, (PauliX, PauliY)):
            raise Exception("Unsupported operation")
        return (model.op1.expr**2 + model.op2.expr**2)**(1/2)

if __name__ == '__main__':
    ac = AnalogCircuit()
    gate = AnalogGate(hamiltonian=2*PauliX()+3*PauliY())
    ac.evolve(gate=gate, duration=1)
    pprint(ac.accept(AnalogIRtoAtomicIR()))
