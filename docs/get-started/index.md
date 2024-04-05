# Welcome to Open Quantum Design
!!! note
    Welcome to the Open Quantum Design frameowkr for programming quantum computers. 
    This documentation is still under development, please feel to contribute! © Open Quantum Design


## Contents
1. [Tutorials](tutorials.md)
2. [How-To Guides](how-to-guides.md)
3. [Reference](reference.md)
4. [Explanation](explanation.md)


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
