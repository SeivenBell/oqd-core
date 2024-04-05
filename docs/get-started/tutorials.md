!!! note

    This part of the project documentation focuses on a
    **learning-oriented** approach. You'll learn how to
    get started with the code in this project.


[//]: # (- Help newcomers with getting started)

[//]: # (- Teach readers about your library by making them)

[//]: # (    write code)

[//]: # (- Inspire confidence through examples that work for)

[//]: # (    everyone, repeatably)

[//]: # (- Give readers an immediate sense of achievement)

[//]: # (- Show concrete examples, no abstractions)

[//]: # (- Provide the minimum necessary explanation)

[//]: # (- Avoid any distractions)


## Analog mode
In analog mode, the central object is an `AnalogCircuit`. An instance of `AnalogCircuit` can be evolved for duration `t` according to an `AnalogGate`. The `AnalogGate` contains a hamiltonian `H` which is an instance of `Operator`. 
As an example, we will perform a Rabi flopping experiment, where one qubit evolves under a driving field.
The (time-independent) Hamiltonian, which govens the quantum evolution, is,
$$
H = \sigma^x
$$
The unitary evolution of the circuit is described by the Hamiltonian, $H$, and the time duration $t$. 
$$
U = e^{i t H}
$$

### Creating an analog quantum circuit
In `quantumion`, time evolution is specified as an **analog gate** (`AnalogGate`).
For example, to implement the one-qubit Rabi flopping from above,
```py
import numpy as np
from quantumion.interface.analog.operator import PauliX
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import AnalogGate, AnalogCircuit

circuit = AnalogCircuit()
gate = AnalogGate(hamiltonian= -(np.pi / 4) * PauliX(), dissipation=Dissipation())
circuit.evolve(
    duration = 1.0,
    gate = H
)
```
In the first lines, we import the relevant objects for analog mode -- the circuit, gate, and operator objects.
The circuit object is composed of analog gates, which requires the `duration` and `hamiltonian` to be specified.

Hamiltonians are represented using Pauli and ladder operators, which act on the qubit registers and boson modes, respectively.

### Defining analog gates
Let's start by creating a more complex Hamiltonian, composed of Pauli operators on the qubit registers.

```py
from quantumion.interface.analog.operator import PauliX
interaction = PauliX() @ PauliX()
``` 
Here, an interaction operator, $\sigma_x \otimes \sigma_x$, 
is defined as the tensor product using the `@` method in Python.
Operator objects `Operator` can (largely) be manipulated like normal Python objects.

!!! Optional

    In our language we represent all operators as abstract syntax trees. this the operator 
    ``` PauliX() @ PauliX()``` 
    would be reprsented as the tree:
    ```mermaid
    graph TD;
        A[@] --> B["PauliX()"]
        A --> C["PauliX()"]
    ```

We will go through concrete examples of how to get started with this in Analog Demos

## Digital mode
Digital quantum circuits, or the gate-based model.
```py
import numpy as np
from quantumion.digital.circuit import DigitalCircuit
from quantumion.digital.gate import Gate, H, CNOT

circuit = DigitalCircuit()
circuit.add(H)
```


## Atomic mode

## Classical emulators
Each mode has a suite of backend classical emulators for designing, 
benchmarking, and studying programs run on quantum computers.

```py
from backends.analog import QutipBackend
from backends.task import Task, TaskArgsAnalog

backend = QutipBackend()
backend.run(task)
```




