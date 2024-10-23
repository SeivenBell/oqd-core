## Introduction

We have a sample compiler for Analog to Atomic levels for the single qubit Rabi Flopping for Hamiltonians of the form

$$
H = A(t)\sigma_{x} + B(t)\sigma_{y}
$$

where coefficients $A$ and $B$ can be time-dependent or time-independent.

## Mathematics

Then we do the following calculations to find the Rabi Frequency and phase:

$$
\Omega(t) = \sqrt{A^{2}(t)+B^{2}(t)}
$$

$$
\frac{\Omega_{1}(t)\Omega_{2}(t)}{2\Delta} = \Omega(t), \quad \Omega_{1}(t) = \Omega_2(t)
$$

Here, $\Delta = 2\pi\hbar c(\frac{1}{\lambda_1} - \frac{1}{\lambda_2})$ where $\lambda_{1} = 355nm$ and $\lambda_{2} = 369nm$.

Now for phase calculation we do $\phi_{1}(t) = 0.5 * \arctan \left( \frac{A(t)}{B(t)} \right)$ with $\phi_{1}(t) = -\phi_{2}(t)$

## Compilations levels

The list below shows the corresponding Atomic Layer objects produced from different Analog Layer objects.

```
Task (Analog) -> Task (Atomic)
AnalogCircuit -> AtomicCircuit
Evolve -> Protocol (a field of AtomicCircuit)
```

## Example

An example Analog Circuit to Atomic Circuit conversion is given here.
Consider an AnalogCircuit composed of the hamiltonian:

$$
H = 2X+3Y+3Y
$$

This hamiltonian is first canoncalized to form

$$
H = 2X+(3+3)Y
$$

and let us evolve that hamiltonian using:

```py
ac = AnalogCircuit()
ac.evolve(gate = AnalogGate(hamiltonian=H), duration = 1.0)
```

This hamiltonian is in canonical form and then the compiler produces

/// tab | Task Level

<!-- prettier-ignore -->
//// admonition | Note
    type: note

`Task` contains program (`AtomicCircuit`) and args (`TaskArgsAtomic`)

////

```py
Task(
    program=AtomicCircuit(
        class_='AtomicCircuit',
        system=System(
            class_='System',
            ions=[
                Ion(
                    class_='Ion',
                    mass=1.0,
                    charge=1.0,
                    levels=[Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0)],
                    transitions=[
                        Transition(
                            class_='Transition',
                            level1=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            level2=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            einsteinA=1.0
                        )
                    ]
                )
            ],
            modes=[Mode(class_='Mode', energy=1.0)]
        ),
        protocol=ParallelProtocol(
            class_='ParallelProtocol',
            sequence=[
                Pulse(
                    class_='Pulse',
                    beam=Beam(
                        class_='Beam',
                        transition=Transition(
                            class_='Transition',
                            level1=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            level2=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            einsteinA=1.0
                        ),
                        rabi=MathPow(
                            class_='MathPow',
                            expr1=MathMul(
                                class_='MathMul',
                                expr1=MathMul(
                                    class_='MathMul',
                                    expr1=MathPow(
                                        class_='MathPow',
                                        expr1=MathAdd(
                                            class_='MathAdd',
                                            expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                            expr2=MathPow(
                                                class_='MathPow',
                                                expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                                expr2=MathNum(class_='MathNum', value=2)
                                            )
                                        ),
                                        expr2=MathNum(class_='MathNum', value=0.5)
                                    ),
                                    expr2=MathNum(class_='MathNum', value=2)
                                ),
                                expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                            ),
                            expr2=MathNum(class_='MathNum', value=0.5)
                        ),
                        detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                        phase=MathDiv(
                            class_='MathDiv',
                            expr1=MathFunc(
                                class_='MathFunc',
                                func='atan',
                                expr=MathDiv(
                                    class_='MathDiv',
                                    expr1=MathNum(class_='MathNum', value=2),
                                    expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3))
                                )
                            ),
                            expr2=MathNum(class_='MathNum', value=2)
                        ),
                        polarization=[-1.0, 1.0],
                        wavevector=[0.0, 0.0, 1.0],
                        target=0
                    ),
                    duration=1.0
                ),
                Pulse(
                    class_='Pulse',
                    beam=Beam(
                        class_='Beam',
                        transition=Transition(
                            class_='Transition',
                            level1=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            level2=Level(
                                class_='Level',
                                principal=None,
                                spin=None,
                                orbital=None,
                                nuclear=None,
                                spin_orbital=None,
                                spin_orbital_nuclear=None,
                                spin_orbital_nuclear_magnetization=None,
                                energy=100.0
                            ),
                            einsteinA=1.0
                        ),
                        rabi=MathPow(
                            class_='MathPow',
                            expr1=MathMul(
                                class_='MathMul',
                                expr1=MathMul(
                                    class_='MathMul',
                                    expr1=MathPow(
                                        class_='MathPow',
                                        expr1=MathAdd(
                                            class_='MathAdd',
                                            expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                            expr2=MathPow(
                                                class_='MathPow',
                                                expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                                expr2=MathNum(class_='MathNum', value=2)
                                            )
                                        ),
                                        expr2=MathNum(class_='MathNum', value=0.5)
                                    ),
                                    expr2=MathNum(class_='MathNum', value=2)
                                ),
                                expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                            ),
                            expr2=MathNum(class_='MathNum', value=0.5)
                        ),
                        detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                        phase=MathDiv(
                            class_='MathDiv',
                            expr1=MathMul(
                                class_='MathMul',
                                expr1=MathNum(class_='MathNum', value=-1),
                                expr2=MathFunc(
                                    class_='MathFunc',
                                    func='atan',
                                    expr=MathDiv(
                                        class_='MathDiv',
                                        expr1=MathNum(class_='MathNum', value=2),
                                        expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3))
                                    )
                                )
                            ),
                            expr2=MathNum(class_='MathNum', value=2)
                        ),
                        polarization=[-1.0, 1.0],
                        wavevector=[0.0, 0.0, 1.0],
                        target=0
                    ),
                    duration=1.0
                )
            ]
        )
    ),
    args=TaskArgsAnalog(layer='analog', n_shots=10, fock_cutoff=4, dt=0.1, metrics={})
)
```

///

/// tab | Circuit Level

<!-- prettier-ignore -->
//// admonition | Note
    type: note

`AtomicCitcuit` contains:

```py
class AtomicCircuit:
    system: System
    protocol: Protocol
```

////

```py
AtomicCircuit(
    class_='AtomicCircuit',
    system=System(
        class_='System',
        ions=[
            Ion(
                class_='Ion',
                mass=1.0,
                charge=1.0,
                levels=[Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0)],
                transitions=[
                    Transition(
                        class_='Transition',
                        level1=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        level2=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        einsteinA=1.0
                    )
                ]
            )
        ],
        modes=[Mode(class_='Mode', energy=1.0)]
    ),
    protocol=ParallelProtocol(
        class_='ParallelProtocol',
        sequence=[
            Pulse(
                class_='Pulse',
                beam=Beam(
                    class_='Beam',
                    transition=Transition(
                        class_='Transition',
                        level1=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        level2=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        einsteinA=1.0
                    ),
                    rabi=MathPow(
                        class_='MathPow',
                        expr1=MathMul(
                            class_='MathMul',
                            expr1=MathMul(
                                class_='MathMul',
                                expr1=MathPow(
                                    class_='MathPow',
                                    expr1=MathAdd(
                                        class_='MathAdd',
                                        expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                        expr2=MathPow(
                                            class_='MathPow',
                                            expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                            expr2=MathNum(class_='MathNum', value=2)
                                        )
                                    ),
                                    expr2=MathNum(class_='MathNum', value=0.5)
                                ),
                                expr2=MathNum(class_='MathNum', value=2)
                            ),
                            expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                        ),
                        expr2=MathNum(class_='MathNum', value=0.5)
                    ),
                    detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                    phase=MathDiv(
                        class_='MathDiv',
                        expr1=MathFunc(
                            class_='MathFunc',
                            func='atan',
                            expr=MathDiv(class_='MathDiv', expr1=MathNum(class_='MathNum', value=2), expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)))
                        ),
                        expr2=MathNum(class_='MathNum', value=2)
                    ),
                    polarization=[-1.0, 1.0],
                    wavevector=[0.0, 0.0, 1.0],
                    target=0
                ),
                duration=1.0
            ),
            Pulse(
                class_='Pulse',
                beam=Beam(
                    class_='Beam',
                    transition=Transition(
                        class_='Transition',
                        level1=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        level2=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                        einsteinA=1.0
                    ),
                    rabi=MathPow(
                        class_='MathPow',
                        expr1=MathMul(
                            class_='MathMul',
                            expr1=MathMul(
                                class_='MathMul',
                                expr1=MathPow(
                                    class_='MathPow',
                                    expr1=MathAdd(
                                        class_='MathAdd',
                                        expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                        expr2=MathPow(
                                            class_='MathPow',
                                            expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                            expr2=MathNum(class_='MathNum', value=2)
                                        )
                                    ),
                                    expr2=MathNum(class_='MathNum', value=0.5)
                                ),
                                expr2=MathNum(class_='MathNum', value=2)
                            ),
                            expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                        ),
                        expr2=MathNum(class_='MathNum', value=0.5)
                    ),
                    detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                    phase=MathDiv(
                        class_='MathDiv',
                        expr1=MathMul(
                            class_='MathMul',
                            expr1=MathNum(class_='MathNum', value=-1),
                            expr2=MathFunc(
                                class_='MathFunc',
                                func='atan',
                                expr=MathDiv(class_='MathDiv', expr1=MathNum(class_='MathNum', value=2), expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)))
                            )
                        ),
                        expr2=MathNum(class_='MathNum', value=2)
                    ),
                    polarization=[-1.0, 1.0],
                    wavevector=[0.0, 0.0, 1.0],
                    target=0
                ),
                duration=1.0
            )
        ]
    )
)
```

///
/// tab | Protocol level

<!-- prettier-ignore -->
//// admonition | Note
    type: note

`Protocol` can be `SequentialProtocol` or `ParallelProtocol`. Here we only have one evolve statement and thus this is a `ParallelProcol`. In the case when we have multiple `Evolve` statements, we will have something like `SequentialProtocol`(`ParallelProcol_1`, `ParallelProcol_2`, ...).

`ParallelProtocol` contains sequence of `Pulse` and `Pulse` comprises one `Beam` object and the `duration` the beam is applied for. Rebi frequency and Phase of the Beam are computed on the fly using the Math described above.
////

```py
ParallelProtocol(
    class_='ParallelProtocol',
    sequence=[
        Pulse(
            class_='Pulse',
            beam=Beam(
                class_='Beam',
                transition=Transition(
                    class_='Transition',
                    level1=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                    level2=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                    einsteinA=1.0
                ),
                rabi=MathPow(
                    class_='MathPow',
                    expr1=MathMul(
                        class_='MathMul',
                        expr1=MathMul(
                            class_='MathMul',
                            expr1=MathPow(
                                class_='MathPow',
                                expr1=MathAdd(
                                    class_='MathAdd',
                                    expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                    expr2=MathPow(
                                        class_='MathPow',
                                        expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                        expr2=MathNum(class_='MathNum', value=2)
                                    )
                                ),
                                expr2=MathNum(class_='MathNum', value=0.5)
                            ),
                            expr2=MathNum(class_='MathNum', value=2)
                        ),
                        expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                    ),
                    expr2=MathNum(class_='MathNum', value=0.5)
                ),
                detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                phase=MathDiv(
                    class_='MathDiv',
                    expr1=MathFunc(
                        class_='MathFunc',
                        func='atan',
                        expr=MathDiv(
                            class_='MathDiv',
                            expr1=MathNum(class_='MathNum', value=2),
                            expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3))
                        )
                    ),
                    expr2=MathNum(class_='MathNum', value=2)
                ),
                polarization=[-1.0, 1.0],
                wavevector=[0.0, 0.0, 1.0],
                target=0
            ),
            duration=1.0
        ),
        Pulse(
            class_='Pulse',
            beam=Beam(
                class_='Beam',
                transition=Transition(
                    class_='Transition',
                    level1=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                    level2=Level(class_='Level', principal=None, spin=None, orbital=None, nuclear=None, spin_orbital=None, spin_orbital_nuclear=None, spin_orbital_nuclear_magnetization=None, energy=100.0),
                    einsteinA=1.0
                ),
                rabi=MathPow(
                    class_='MathPow',
                    expr1=MathMul(
                        class_='MathMul',
                        expr1=MathMul(
                            class_='MathMul',
                            expr1=MathPow(
                                class_='MathPow',
                                expr1=MathAdd(
                                    class_='MathAdd',
                                    expr1=MathPow(class_='MathPow', expr1=MathNum(class_='MathNum', value=2), expr2=MathNum(class_='MathNum', value=2)),
                                    expr2=MathPow(
                                        class_='MathPow',
                                        expr1=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3)),
                                        expr2=MathNum(class_='MathNum', value=2)
                                    )
                                ),
                                expr2=MathNum(class_='MathNum', value=0.5)
                            ),
                            expr2=MathNum(class_='MathNum', value=2)
                        ),
                        expr2=MathNum(class_='MathNum', value=1.334829730528359e-19)
                    ),
                    expr2=MathNum(class_='MathNum', value=0.5)
                ),
                detuning=MathNum(class_='MathNum', value=1.334829730528359e-19),
                phase=MathDiv(
                    class_='MathDiv',
                    expr1=MathMul(
                        class_='MathMul',
                        expr1=MathNum(class_='MathNum', value=-1),
                        expr2=MathFunc(
                            class_='MathFunc',
                            func='atan',
                            expr=MathDiv(
                                class_='MathDiv',
                                expr1=MathNum(class_='MathNum', value=2),
                                expr2=MathAdd(class_='MathAdd', expr1=MathNum(class_='MathNum', value=3), expr2=MathNum(class_='MathNum', value=3))
                            )
                        )
                    ),
                    expr2=MathNum(class_='MathNum', value=2)
                ),
                polarization=[-1.0, 1.0],
                wavevector=[0.0, 0.0, 1.0],
                target=0
            ),
            duration=1.0
        )
    ]
)
```

///
