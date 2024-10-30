The analog interface represents a quantum experiment in terms of time evolving Hamiltonians.

## Quantum Degrees of Freedom

In this analog interface, we allow for 2 different quantum degrees of freedom:

/// tab | Qubits
Qubits consist of a pair of states (spin $\uparrow$ and spin $\downarrow$).
///
/// tab | Bosonic
Bosonic degrees of freedom form a fock space.
///

## Operators

/// tab | Pauli

The basis of operators for the qubits are the Pauli operators:

- $\sigma^I$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.PauliI] </div>
- $\sigma^x$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.PauliX] </div>
- $\sigma^y$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.PauliY] </div>
- $\sigma^z$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.PauliZ] </div>

///

/// tab | Ladder

The basis of operators for the bosonic degree of freedom are the ladder operators:

- $a$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.Annihilation] </div>
- $a^{\dagger}$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.Creation] </div>
- $I$ <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.Identity] </div>

///

### Operator Operations

The basis operators can be combined with the operations:

- Addition <div style="float:right"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.OperatorAdd] </div>

- Multiplication <div style="float:right"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.OperatorMul] </div>

- Tensor Product <div style="float:right"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.OperatorKron] </div>

- Scalar Multiplication <div style="float:right"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operator.OperatorScalarMul] </div>

## Hamiltonian

The Hamiltonian is an operator that governs interactions between quantum degrees of freedom.

The state of the system evolves under the unitary:

$$
U = e^{i H t}
$$

<!-- prettier-ignore -->
/// admonition | Example
    type: example
Spin-dependent force Hamiltonian:

$$
H = \sigma^+ \otimes a + \sigma^- \otimes a^{\dagger}
$$

```py
H = PauliPlus() @ Annihilation() + PauliMinus() @ Creation()
```

///

## Analog Gate <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operation.AnalogGate] </div>

The [AnalogGate][oqd_core.interface.analog.operation.AnalogGate] wraps the Hamiltonian.

```py
gate = AnalogGate(hamiltonian=H)
```

<!-- prettier-ignore -->
/// admonition | Note
    type: note
The purpose of the [AnalogGate][oqd_core.interface.analog.operation.AnalogGate] is to accomodate dissipation during the time evolution in the future.
///

## Analog Circuit <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operation.AnalogCircuit] </div>

The [AnalogCircuit][oqd_core.interface.analog.operation.AnalogCircuit] is the top level structure that describes a quantum experiment at the analog layer.

An [AnalogCircuit][oqd_core.interface.analog.operation.AnalogCircuit] consist of different kinds of statements:

/// tab | Initialize

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operation.Initialize]
////

Initializes all quantum degrees of freedom in the experiment:

- Qubits $\rightarrow$ $| \downarrow \rangle$
- Bosons $\rightarrow$ $| 0 \rangle$

<!-- prettier-ignore -->
//// admonition | Not Implemented
    type: warning
Initialize describes a global initialization. There is no support for individual initialization currently.
////
///

/// tab | Evolve

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operation.Evolve]
////

Evolve desribes the evolution of the system with an AnalogGate for a set duration.
///

/// tab | Measure

//// html | div[style='float: right']
[![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_core.interface.analog.operation.Measure]
////

Performs a projective measurement of all quantum degrees of freedom.

<!-- prettier-ignore -->
//// admonition | Not Implemented
    type: warning
Measure describes a global measurement. There is no support for individual measurement currently.
////
///

## Usage

<!-- prettier-ignore -->
/// admonition | Example
    type: example

```py
circuit = AnalogCircuit()

circuit.initialize()
circuit.evolve(gate, duration=1)
circuit.measure()
```

///
