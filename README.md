# ![Open Quantum Design](docs/img/oqd-logo-text.png)

<h2 align="center">
    Program the world's first open-source, full-stack quantum computer.
</h2>

[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
[![CI](https://github.com/OpenQuantumDesign/oqd-core/actions/workflows/CI.yml/badge.svg)](https://github.com/OpenQuantumDesign/oqd-core/actions/workflows/CI.yml)

## What's here

- [Quick Start](#quickstart) <br/>
- [Installation](#installation) <br/>
- [The Stack](#stack) <br/>
- [Documentation](#documentation) <br/>

## Quick start

## Installation <a name="installation"></a>

First install the OQD compiler infrastructure with:

```bash
pip install git+https://github.com/OpenQuantumDesign/compiler_infrastructure.git
```

then:

```bash
pip install git+https://github.com/OpenQuantumDesign/oqd-core.git
```

Or clone the repository locally and install with:

```bash
git clone https://github.com/OpenQuantumDesign/oqd-core
pip install .
```

## Getting Started <a name="Getting Started"></a>

To get started you can run one of the example scripts provided. For example, to run the 3 qubit GHz state protocol you can run:

```python
import matplotlib.pyplot as plt

from oqd_core.interface.analog.operator import *
from oqd_core.interface.analog.operations import *
from oqd_core.backend.metric import *
from oqd_core.backend.task import Task
from oqd_analog_emulator.base import TaskArgsAnalogSimulator
from oqd_core.backend import QutipBackend

X = PauliX()
Z = PauliZ()

Hx = AnalogGate(hamiltonian=X)

circuit = AnalogCircuit()
circuit.evolve(duration=10, gate=Hx)

args = TaskArgsAnalogSimulator(
  n_shots=100,
  fock_cutoff=4,
  metrics={"Z": Expectation(operator=Z)},
  dt=1e-3,
)

task = Task(program=circuit, args=args)

backend = QutipBackend()
experiment = backend.compile(task=task)
results = backend.run(experiment=experiment)

plt.plot(results.times, results.metrics["Z"], label=f"$\\langle Z \\rangle$")
```

## The stack <a name="stack"></a>

```mermaid
block-beta
   columns 3
   
   block:Interface
       columns 1
       InterfaceTitle("<i><b>Interfaces</b><i/>")
       InterfaceDigital["<b>Digital Interface</b>\nQuantum circuits with discrete gates"] 
       space
       InterfaceAnalog["<b>Analog Interface</b>\n Continuous-time evolution with Hamiltonians"] 
       space
       InterfaceAtomic["<b>Atomic Interface</b>\nLight-matter interactions between lasers and ions"]
       space
    end
    
    block:IR
       columns 1
       IRTitle("<i><b>IRs</b><i/>")
       IRDigital["Quantum circuit IR\nopenQASM, LLVM+QIR"] 
       space
       IRAnalog["openQSIM"]
       space
       IRAtomic["openAPL"]
       space
    end
    
    block:Emulator
       columns 1
       EmulatorsTitle("<i><b>Classical Emulators</b><i/>")
       
       EmulatorDigital["Pennylane, Qiskit"] 
       space
       EmulatorAnalog["QuTiP, QuantumOptics.jl"]
       space
       EmulatorAtomic["TrICal, QuantumIon.jl"]
       space
    end
    
    space
    block:RealTime
       columns 1
       RealTimeTitle("<i><b>Real-Time</b><i/>")
       space
       RTSoftware["ARTIQ, DAX, OQDAX"] 
       space
       RTGateware["Sinara Real-Time Control"]
       space
       RTHardware["Lasers, Modulators, Photodetection, Ion Trap"]
       space
       RTApparatus["Trapped-Ion QPU (<sup>171</sup>Yt<sup>+</sup>, <sup>133</sup>Ba<sup>+</sup>)"]
       space
    end
    space
    
   InterfaceDigital --> IRDigital
   InterfaceAnalog --> IRAnalog
   InterfaceAtomic --> IRAtomic
   
   IRDigital --> IRAnalog
   IRAnalog --> IRAtomic
   
   IRDigital --> EmulatorDigital
   IRAnalog --> EmulatorAnalog
   IRAtomic --> EmulatorAtomic
   
   IRAtomic --> RealTimeTitle
   
   RTSoftware --> RTGateware
   RTGateware --> RTHardware
   RTHardware --> RTApparatus
   
   classDef title fill:#d6d4d4,stroke:#333;
   classDef digital fill:#E7E08B,stroke:#333;
   classDef analog fill:#E4E9B2,stroke:#333;
   classDef atomic fill:#D2E4C4,stroke:#333;
   classDef realtime fill:#B5CBB7,stroke:#333;

    classDef highlight fill:#f2bbbb,stroke:#333,stroke-dasharray: 5 5;

    class InterfaceTitle,IRTitle,EmulatorsTitle,RealTimeTitle title
    class InterfaceDigital,IRDigital,EmulatorDigital digital
    class InterfaceAnalog,IRAnalog,EmulatorAnalog analog
    class InterfaceAtomic,IRAtomic,EmulatorAtomic atomic
    class RTSoftware,RTGateware,RTHardware,RTApparatus realtime
   
   class EmulatorAnalog,Interface highlight
```

### Interfaces <a name="frontends"></a>

Python packages for each layer of the stack.

### Intermediate representations <a name="intermediate-representations"></a>

Expressed with [Pydantic](https://docs.pydantic.dev/latest/).

#### Software <a name="software"></a>

Planned supported software backends include:

- Digital Circuit
  - [Tensor Circuit](https://github.com/tencent-quantum-lab/tensorcircuit)
  - [Yao](https://yaoquantum.org/)
- Analog Circuit
  - [Qutip](https://qutip.org/)
  - [QuantumOptics.jl](https://docs.qojulia.org/search/?q=calcium)
- Trapped-ion Physics Simulator
  - [IonSim.jl](https://www.ionsim.org/)

#### Hardware <a name="hardware"></a>

Planned supported hardware backends include:

- [Quantum Information with Trapped-ions (QITI Lab)](https://qiti.iqc.uwaterloo.ca/publications/) Blade Trap $\left( ^{171}\mathrm{Yb}^+ \right)$
- [QuantumIon](https://tqt.uwaterloo.ca/project-details/quantumion-an-open-access-quantum-computing-platform/) $\left( ^{138}\mathrm{Ba}^+ \right)$

## Documentation <a name="documentation"></a>

Documentation is implemented with [MkDocs](https://www.mkdocs.org/) and can be read from the [docs](https://github.com/OpenQuantumDesign/oqd-core/tree/main/docs) folder.

To install the dependencies for documentation, run:

```
pip install -e ".[docs]"
```

To deploy the documentation server locally:

```
cp -r examples/ docs/examples/
mkdocs serve
```

After deployment, the documentation can be accessed from http://127.0.0.1:8000

### Where in the stack
```mermaid
block-beta
   columns 3
   
   block:Interface
       columns 1
       InterfaceTitle("<i><b>Interfaces</b><i/>")
       InterfaceDigital["<b>Digital Interface</b>\nQuantum circuits with discrete gates"] 
       space
       InterfaceAnalog["<b>Analog Interface</b>\n Continuous-time evolution with Hamiltonians"] 
       space
       InterfaceAtomic["<b>Atomic Interface</b>\nLight-matter interactions between lasers and ions"]
       space
    end
    
    block:IR
       columns 1
       IRTitle("<i><b>IRs</b><i/>")
       IRDigital["Quantum circuit IR\nopenQASM, LLVM+QIR"] 
       space
       IRAnalog["openQSIM"]
       space
       IRAtomic["openAPL"]
       space
    end
    
    block:Emulator
       columns 1
       EmulatorsTitle("<i><b>Classical Emulators</b><i/>")
       
       EmulatorDigital["Pennylane, Qiskit"] 
       space
       EmulatorAnalog["QuTiP, QuantumOptics.jl"]
       space
       EmulatorAtomic["TrICal, QuantumIon.jl"]
       space
    end
    
    space
    block:RealTime
       columns 1
       RealTimeTitle("<i><b>Real-Time</b><i/>")
       space
       RTSoftware["ARTIQ, DAX, OQDAX"] 
       space
       RTGateware["Sinara Real-Time Control"]
       space
       RTHardware["Lasers, Modulators, Photodetection, Ion Trap"]
       space
       RTApparatus["Trapped-Ion QPU (<sup>171</sup>Yt<sup>+</sup>, <sup>133</sup>Ba<sup>+</sup>)"]
       space
    end
    space
    
   InterfaceDigital --> IRDigital
   InterfaceAnalog --> IRAnalog
   InterfaceAtomic --> IRAtomic
   
   IRDigital --> IRAnalog
   IRAnalog --> IRAtomic
   
   IRDigital --> EmulatorDigital
   IRAnalog --> EmulatorAnalog
   IRAtomic --> EmulatorAtomic
   
   IRAtomic --> RealTimeTitle
   
   RTSoftware --> RTGateware
   RTGateware --> RTHardware
   RTHardware --> RTApparatus
   
   classDef title fill:#d6d4d4,stroke:#333;
   classDef digital fill:#E7E08B,stroke:#333;
   classDef analog fill:#E4E9B2,stroke:#333;
   classDef atomic fill:#D2E4C4,stroke:#333;
   classDef realtime fill:#B5CBB7,stroke:#333;

    classDef highlight fill:#f2bbbb,stroke:#333,stroke-dasharray: 5 5;

    class InterfaceTitle,IRTitle,EmulatorsTitle,RealTimeTitle title
    class InterfaceDigital,IRDigital,EmulatorDigital digital
    class InterfaceAnalog,IRAnalog,EmulatorAnalog analog
    class InterfaceAtomic,IRAtomic,EmulatorAtomic atomic
    class RTSoftware,RTGateware,RTHardware,RTApparatus realtime
   
   class Interface,IRAnalog,IRAtomic highlight
```
The stack components highlighted in red are contained in this repository.