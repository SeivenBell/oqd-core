# Copyright 2024 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oqd_compiler_infrastructure import RewriteRule, Pre, Chain

########################################################################################


class UnrollLevelLabel(RewriteRule):
    def map_Ion(self, model):
        self.ion_levels = {level.label: level for level in model.levels}

    def map_Transition(self, model):
        level1 = self.ion_levels[model.level1]
        level2 = self.ion_levels[model.level2]
        return model.__class__(
            label=model.label,
            level1=level1,
            level2=level2,
            einsteinA=model.einsteinA,
            multipole=model.multipole,
        )


class UnrollTransitionLabel(RewriteRule):
    def map_System(self, model):
        self.ions_transitions = [
            {transition.label: transition for transition in ion.transitions}
            for ion in model.ions
        ]

    def map_Beam(self, model):
        transition = self.ions_transitions[model.target][model.transition]
        return model.__class__(
            transition=transition,
            rabi=model.rabi,
            detuning=model.detuning,
            phase=model.phase,
            polarization=model.polarization,
            wavevector=model.wavevector,
            target=model.target,
        )


unroll_label_pass = Chain(
    Pre(UnrollLevelLabel()),
    Pre(UnrollTransitionLabel()),
)

########################################################################################

if __name__ == "__main__":
    import numpy as np

    from oqd_compiler_infrastructure import PrettyPrint, Post

    from oqd_core.interface.atomic import (
        AtomicCircuit,
        SequentialProtocol,
        Pulse,
        Beam,
        System,
        Ion,
        Level,
        Transition,
    )

    downstate = Level(
        label="q0",
        principal=6,
        spin=1 / 2,
        orbital=0,
        nuclear=1 / 2,
        spin_orbital=1 / 2,
        spin_orbital_nuclear=0,
        spin_orbital_nuclear_magnetization=0,
        energy=2 * np.pi * 0,
    )
    estate = Level(
        label="e0",
        principal=5,
        spin=1 / 2,
        orbital=1,
        nuclear=1 / 2,
        spin_orbital=1 / 2,
        spin_orbital_nuclear=1,
        spin_orbital_nuclear_magnetization=-1,
        energy=2 * np.pi * 100,
    )

    transitions = [
        Transition(
            label="q0->e0",
            level1="q0",
            level2="e0",
            einsteinA=1,
            multipole="E1",
        ),
    ]

    ion = Ion(
        mass=171,
        charge=1,
        position=[0, 0, 0],
        levels=[downstate, estate],
        transitions=transitions,
    )

    system = System(
        ions=[
            ion,
        ],
        modes=[],
    )

    beam = Beam(
        transition="q0->e0",
        rabi=2 * np.pi * 1,
        detuning=0,
        phase=0,
        polarization=[1, 0, 0],
        wavevector=[0, 1, 0],
        target=0,
    )

    protocol = SequentialProtocol(
        sequence=[
            Pulse(beam=beam, duration=1),
        ]
    )

    atomic_circuit = AtomicCircuit(system=system, protocol=protocol)

    print(Post(PrettyPrint())(unroll_label_pass(atomic_circuit)))
