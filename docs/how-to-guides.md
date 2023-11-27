# How-to: A hands on guide
!!! note

    This part of the project documentation focuses on a
    **problem-oriented** approach. You'll tackle common
    tasks that you might have, with the help of the code
    provided in this project.

## Analog
Let's implement our favourite Hamiltonian -- the transverse-field Ising model.
The general Hamiltonian looks like,
$$
H = \sum_{\langle ij \rangle} \sigma^x_i \sigma^x_j + h \sum_i \sigma^z_i
$$

Let's implement it with two qubits and with $h=1$.
$$
H = \sigma^x_1 \sigma^x_2 + \sigma^z_1 + \sigma^z_2
$$

Our analog circuit will have one gate, which describes this Hamiltonian.
``` py
from quantumion.analog import AnalogCircuit, AnalogGate, PauliX, PauliZ, PauliI

circuit = AnalogCircuit()
circuit.evolve(
    AnalogGate(
        duration=1.0, 
        hamiltonian=[PauliX @ PauliX, PauliZ @ PauliI, PauliI @ PauliZ],
    )
)    
```

Let's now generalize this to 
``` py
from quantumion.analog import AnalogCircuit, AnalogGate, PauliX, PauliZ, PauliI

n = 10
circuit = AnalogCircuit()
hamiltonian = []
for i in range(n):
    interaction = tensor([PauliX if i in (i, (i+1)%n) else PauliI for i in range(n)])
    field = tensor([PauliZ if i in (i, (i+1)%n) else PauliI for i in range(n)])
    hamiltonian += [interaction, field]

circuit.evolve(
    AnalogGate(
        duration=1.0, 
        hamiltonian=hamiltonian
    )
)    
```


## Digital


## Atomic
