import numpy as np

from quantumion.interface.atomic import (
    Level,
    Transition,
    Multipole,
    Ion,
    Register,
    Pulse,
    Protocol,
    Apply,
    AtomicProgram,
)
from quantumion.compiler.atomic import AtomicProgramIonsAnalysis

########################################################################################

if __name__ == "__main__":

    dark_state = Level(
        principal=6,
        spin=0.5,
        orbital=0,
        nuclear=0.5,
        spin_orbital=0.5,
        spin_orbital_nuclear=0,
        spin_orbital_nuclear_magnetization=0,
        energy=0,
    )
    bright_state = Level(
        principal=6,
        spin=0.5,
        orbital=0,
        nuclear=0.5,
        spin_orbital=0.5,
        spin_orbital_nuclear=1,
        spin_orbital_nuclear_magnetization=0,
        energy=12.6428e9,
    )
    excited_state = Level(
        principal=6,
        spin=0.5,
        orbital=1,
        nuclear=0.5,
        spin_orbital=0.5,
        spin_orbital_nuclear=0,
        spin_orbital_nuclear_magnetization=0,
        energy=811.29e12,
    )
    excited_state_2 = Level(
        principal=6,
        spin=0.5,
        orbital=1,
        nuclear=0.5,
        spin_orbital=0.5,
        spin_orbital_nuclear=1,
        spin_orbital_nuclear_magnetization=0,
        energy=811.29e12 + 2.105e9,
    )
    transition_1 = Transition(
        level1=dark_state,
        level2=excited_state_2,
        multipole=Multipole(field="E", pole=1),
        einstein_A=1,
    )
    transition_2 = Transition(
        level1=bright_state,
        level2=excited_state,
        multipole=Multipole(field="E", pole=1),
        einstein_A=1,
    )

    yb171plus = Ion(
        mass=171,
        charge=1,
        levels=[dark_state, bright_state, excited_state, excited_state_2],
        transitions=[transition_1, transition_2],
    )

    reg = Register(configuration=[yb171plus, yb171plus])

    raman1 = Pulse(
        transition=yb171plus.transitions[0],
        rabi=1e6 * 2 * np.pi,
        detuning=1e9,
        phase=np.pi / 2,
        polarization=[1, 0, 0],
        wavevector=[0, 0, 1],
        targets=[0, 1],
    )
    raman2 = Pulse(
        transition=yb171plus.transitions[1],
        rabi=1e6 * 2 * np.pi,
        detuning=1e9,
        phase=np.pi / 2,
        polarization=[0, 0, 1],
        wavevector=[0, 0, 1],
        targets=[0, 1],
    )

    twophotonraman = Protocol(pulses=[raman1, raman2])

    program = AtomicProgram(
        statements=[
            reg,
            Apply(protocol=twophotonraman, time=0.5e-6),
        ]
    )

    apia = AtomicProgramIonsAnalysis()
    program.accept(apia)
    print(apia.ions)
