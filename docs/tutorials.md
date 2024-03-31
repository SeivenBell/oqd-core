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
In analog mode, the central object is an `AnalogCircuit`. 
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
In `quantumion`, time evolution is specified as an **analog gate** ([`AnalogGate`](reference.md)).
For example, to implement the one-qubit Rabi flopping from above,
```py
import numpy as np
from quantumion.interface.analog.circuit  import  AnalogCircuit
from quantumion.interface.analog.gate     import  AnalogGate
from quantumion.interface.analog.operator import  PauliX, PauliZ, PauliI

circuit = AnalogCircuit()
circuit.evolve(
    AnalogGate(
        duration=1.0, 
        hamiltonian=[np.pi * PauliX],
    )
)
```
In the first lines, we import the relevant objects for analog mode -- the circuit, gate, and operator objects.
The circuit object is composed of analog gates, which requires the `duration` and `hamiltonian` to be specified.

Hamiltonians are represented using Pauli and ladder operators, which act on the qubit registers and boson modes, respectively.

### Defining analog gates
Let's start by creating a more complex Hamiltonian, composed of Pauli operators on the qubit registers.
```py
from quantumion.interface.analog.operator import  PauliX, PauliY, PauliZ, PauliI

print(PauliX * PauliX == PauliI)
print(PauliY * PauliY == PauliI)
print(PauliZ * PauliZ == PauliI)
```

```py
from quantumion.interface.analog.operator import PauliX
interaction = PauliX @ PauliX
``` 
Here, an interaction operator, $\sigma_x \otimes \sigma_x$, 
is defined as the tensor product using the `@` method in Python.
Operator objects [`Operator`](reference.md) can (largely) be manipulated like normal Python objects.
```py
from quantumion.interface.analog.operator import PauliX
print(PauliX + PauliX == 2 * PauliX)
>>> True
``` 


## Digital mode
Digital quantum circuits, or the gate-based model.
```py
import numpy as np
from quantumion.interface.digital.circuit import DigitalCircuit
from quantumion.interface.digital.gate import Gate, H, CNOT

circuit_digital = DigitalCircuit()
circuit_digital.add(H)
```


## Atomic mode

## Classical emulators
Each mode has a suite of backend classical emulators for designing, 
benchmarking, and studying programs run on quantum computers.

```py
from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.analog.julia.quantumoptics import QuantumOpticsBackend
from quantumion.backend.task import Task, TaskArgsAnalog

args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    dt=0.01,
)
task = Task(program=circuit, args=args)
backend = QutipBackend()
result = backend.run(task)
```




