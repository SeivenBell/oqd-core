# Welcome to Open Quantum Design
!!! note
    Welcome to the Open Quantum Design frameowkr for programming quantum computers. 
    This documentation is still under development, please feel to contribute! © Open Quantum Design


# ![Open Quantum Design](docs/img/oqd-logo-text.png)


## The stack
```mermaid
flowchart LR
    Digital[Digital Circuit] --> openQASM(openQASM) 
    
    Analog[Analog Circuit] --> openQSIM(openQSIM)
    Atomic[Atomic Protocol] ---> openAPL(openAPL)
  
    openQSIM --> |compile| openAPL
    openQASM --> |compile| openAPL

    openQSIM ----> Qutip
    openQSIM ----> Quantumoptics.jl

    openQASM ----> TensorCircuit
    openQASM ----> PastaQ.jl
    
    openAPL ---> Hardware{Bare metal}
    openAPL ---> IonSim.jl
```

[//]: # ({%)

[//]: # (   include-markdown "../examples/bell_state.ipynb")

[//]: # (%})