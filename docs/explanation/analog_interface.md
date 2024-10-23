The analog interface represents a quantum experiment expressed by time evolving Hamiltonians.

## Analog mode
As an example, consider a Rabi flopping experiment, where one qubit evolves under a driving field.
The (time-independent) Hamiltonian, which governs the quantum evolution, is,

$$
H = \sigma^x
$$

The unitary evolution of the circuit is described by the Hamiltonian, $H$, and the time duration $t$.

$$
U = e^{i t H}
$$

### Creating an analog quantum circuit
In the Analog interface, the central object is an `AnalogCircuit`.
Time evolution is specified as an `AnalogGate`, which defines a Hamiltonian applied for a finite `duration`.
For example, to implement the one-qubit Rabi flopping from above,
```py
import numpy as np
from oqd_core.interface.analog.operator import PauliX
from oqd_core.interface.analog.operation import AnalogGate, AnalogCircuit

circuit = AnalogCircuit()
gate = AnalogGate(hamiltonian=-(np.pi / 4) * PauliX())
circuit.evolve(
    duration=1.0,
    gate=gate
)
```

In the first lines, we import the relevant objects for analog mode -- the circuit, gate, and operator objects.
The circuit object is composed of analog gates, which requires the `duration` and `hamiltonian` to be specified.

Hamiltonians are represented using Pauli and ladder operators, which act on the qubit registers and boson modes, respectively.

### Defining analog gates

Let's start by creating a more complex Hamiltonian, composed of Pauli operators on the qubit registers.

```py
from oqd_core.interface.analog.operator import PauliX

interaction = PauliX() @ PauliX()
```

Here, an interaction operator, $\sigma_x \otimes \sigma_x$,
is defined as the tensor product using the `@` method in Python.
Operator objects `Operator` can (largely) be manipulated like normal Python objects.

<!-- prettier-ignore -->
/// admonition | Optional
    type: note

In our language we represent all operators as abstract syntax trees. this the operator
` PauliX() @ PauliX()`
would be reprsented as the tree:

```mermaid
graph TD;
    A[@] --> B["PauliX()"]
    A --> C["PauliX()"]
```

///
