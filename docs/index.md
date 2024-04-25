
# ![Open Quantum Design](./img/oqd-logo-text.png)

<div align="center">
    <h2 align="center">
        Program the world's first open-source, full-stack quantum computer.
    </h2>
</div>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
[![GitHub Workflow Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/ki3-qbt/graph-compiler/actions)

!!! note
    Welcome to the Open Quantum Design framework for programming quantum computers. 
    This documentation is still under development, please feel to contribute! © Open Quantum Design


## The stack
```mermaid
flowchart LR

    Digital[<font color=white> Digital Circuit] --> openQASM(<font color=white> openQASM)
    Analog[<font color=white> Analog Circuit] --> openQSIM(<font color=white> openQSIM)
    Atomic[<font color=white> Atomic Protocol] ---> openAPL(<font color=white> openAPL)
  
    openQSIM --> |compile| openAPL
    openQASM --> |compile| openAPL

    openQSIM ----> Qutip(<font color=white> Qutip)
    openQSIM ----> Quantumoptics(<font color=white> QuantumOptics.jl)

    openQASM ----> Qiskit(<font color=white> Qiskit)
    openQASM ----> Yao(<font color=white> Yao.jl)

    openAPL ---> IonSim(<font color=white> IonSim.jl)
    openAPL ---> Hardware{<font color=white> Bare metal}
    
    classDef Interfaces fill:#6db290,stroke:#808080,stroke-width:2px;
    class Digital,Analog,Atomic Interfaces;
    
    classDef IRs fill:#44948f,stroke:#808080,stroke-width:2px;
    class openQASM,openQSIM,openAPL IRs;

    classDef Backends fill:#24768b,stroke:#808080,stroke-width:2px;
    class Qutip,Quantumoptics,Yao,Qiskit,IonSim,Hardware Backends;
    

```
