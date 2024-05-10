from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.interface.analog.operations import *
from quantumion.interface.analog.operator import *
from quantumion.interface.atomic import *
from quantumion.interface.math import MathFunc, MathNum
from quantumion.backend.task import Task, TaskArgsAnalog
import numpy as np
from rich import print as pprint

class AnalogIRtoAtomicIR(AnalogInterfaceTransformer):

    def __init__(self) -> None:
        super().__init__()
        self.delta = 2 * (6.626*(10**(-34))) * np.pi * (3*(10**8)) * ((1/(355*(10**(-9)))) - (1/(369*(10**(-9)))))

    def visit_Task(self, model: Task):
        return Task(program=self.visit(model.program), args=TaskArgsAnalog())

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        level = Level(energy = 100)
        transition = Transition(
            level1 = level,
            level2 = level,
            einsteinA=1.0
        )
        ion = Ion(
            mass = 1,
            charge = 1,
            levels = [level],
            transitions=[transition]
        )
        mode = Mode(
            energy=1
        )
        system = System(
            ions = [ion],
            modes = [mode]
        )

        if len(model.sequence) == 1:
            protocol = self.visit(model.sequence)[0]
        else:
            protocol = SequentialProtocol(
                sequence = self.visit(model.sequence)
            )

        circuit = AtomicCircuit(
            system=system,
            protocol=protocol
        )
        return circuit
    
    def visit_Evolve(self, model: Evolve):
        omega, phi  = self.visit(model.gate.hamiltonian)
        omega_A = (omega*2*self.delta)**(1/2)
        omega_B = omega_A
        phi_A = phi/2
        phi_B = -phi/2
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

        protocol = ParallelProtocol(sequence = [pulse_A, pulse_B])

        return protocol

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if not isinstance(model.op, (PauliX, PauliY)):
            raise Exception("Unsupported operation")
        if isinstance(model.op, PauliX):
            phi = np.pi/2
        else:
            phi = 0
        return (model.expr**2)**(1/2), MathNum(value=phi)

    def visit_OperatorAdd(self, model: OperatorAdd):
        if not isinstance(model.op1.op, (PauliX, PauliY)) or not isinstance(model.op2.op, (PauliX, PauliY)):
            raise Exception("Unsupported operation")
        return (model.op1.expr**2 + model.op2.expr**2)**(1/2), MathFunc(func='atan', expr=model.op1.expr/model.op2.expr)

if __name__ == '__main__':
    ac = AnalogCircuit()
    gate = AnalogGate(hamiltonian=2*PauliX()+3*PauliY())
    gate2 = AnalogGate(hamiltonian=55*PauliX())
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={},
        dt=1e-2,
    )
    task = Task(program=ac, args=args)
    ac.evolve(gate=gate, duration=1)
    # ac.evolve(gate=gate2, duration=3)
    pprint(ac.accept(AnalogIRtoAtomicIR()))
