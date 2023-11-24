!!! note

    This part of the project documentation focuses on a
    **learning-oriented** approach. You'll learn how to
    get started with the code in this project.


- Help newcomers with getting started
- Teach readers about your library by making them
    write code
- Inspire confidence through examples that work for
    everyone, repeatably
- Give readers an immediate sense of achievement
- Show concrete examples, no abstractions
- Provide the minimum necessary explanation
- Avoid any distractions

``` py
from quantumion.analog.circuit import AnalogCircuit
from backends.analog import QutipBackend

circuit = AnalogCircuit()
circuit.evolve(
    AnalogGate(
        duration=1.0, 
        hamiltonian=[PauliX @ PauliX, PauliZ @ PauliI, PauliI @ PauliZ],
    )
)    
```

