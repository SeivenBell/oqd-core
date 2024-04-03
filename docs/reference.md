!!! note

    This part of the project documentation focuses on
    an **information-oriented** approach. Use it as a
    reference for the technical implementation of the
    project code.

## Analog mode

``` mermaid
classDiagram
  AnalogCircuit <|-- Statement
  
  Statement <|-- Initialize
  Statement <|-- Evolve
  Statement <|-- Measure
  
  Evolve <|-- AnalogGate
  AnalogGate <|-- Operator

  class AnalogCircuit{
    .sequence: list[Statement]
  }
  
  class Statement{
    .keyword: string
  }
  class Initialize{
    .keyword: 'initialize'
  }
  class Evolve{
    .keyword: 'evolve'
    .gate: AnalogGate
  }
  class Measure{
    .keyword: 'measure'
  }
  
  class AnalogGate{
    .duration: float
    .hamiltonian: list[Operator]
    .dissipation: list[Dissipation]
  }
  
  class Operator{
    .coefficient: float | complex
    .pauli: list['x', 'y', 'z', 'i']
    .ladder: list[-1, 0 1]
  }
```

::: quantumion.interface.analog.operations.AnalogCircuit

::: quantumion.interface.analog.operations.AnalogGate

::: quantumion.interface.analog.operator.Operator


# Digital mode
::: quantumion.interface.digital.circuit.DigitalCircuit

::: quantumion.interface.digital.gate.Gate


# Atomic mode
