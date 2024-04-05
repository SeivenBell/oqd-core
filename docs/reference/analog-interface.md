
# Analog interface

!!! note

    This part of the project documentation focuses on
    an **information-oriented** approach. Use it as a
    reference for the technical implementation of the
    project code.

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

::: quantumion.interface.analog.operations
    options:
      show_root_heading: true
    show_source: false