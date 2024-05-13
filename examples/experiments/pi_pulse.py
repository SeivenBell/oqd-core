from math import pi

from rich import print as pprint

from quantumion.interface.atomic import *
from quantumion.compiler.atomic import *

PLANCK_CONSTANT = 6.62607015e-34 # J * s
ATOMIC_MASS_UNIT = 1.66053906660e-27 # kg
ELEMENTARY_CHARGE = 1.602176634e-19 # C

def main():
    # define 133Ba+ system extremely simply
    ket0 = Level(energy=PLANCK_CONSTANT * 9_925.4 * 1e6) # J
    ket1 = Level(energy=0) # J
    qubit_transition = Transition(
        level1=ket1,
        level2=ket0,
        einsteinA=0,
    )
    barium133 = Ion(
        mass=133 * ATOMIC_MASS_UNIT, # kg
        charge=ELEMENTARY_CHARGE, # C
        levels=[ket0, ket1],
        transitions=[qubit_transition],
    )
    center_of_mass_mode = Mode(energy=PLANCK_CONSTANT * 2 * pi * 2.3 * 1e6)
    simple_system = System(
        ions=[barium133],
        modes=[center_of_mass_mode],
    )

    # define pi pulse - microwave frequency drive
    microwave = Beam(
        transition=qubit_transition,
        rabi=1e6, # hz
        detuning=0, # hz
        phase=0, # rad
        polarization=[1., 0.],
        wavevector=[1., 0., 0.],
        target=0,
    )
    pi_pulse = Pulse(beam=microwave, duration=1e-6) # s

    # define protocol - in this case, a single pi pulse
    pi_protocol = SequentialProtocol(sequence=[pi_pulse])

    # define circuit
    pi_circuit = AtomicCircuit(
        system=simple_system,
        protocol=pi_protocol,
    )

    pprint(pi_circuit.accept(AtomicToARTIQ()))

if __name__ == "__main__":
    main()
