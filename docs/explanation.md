
!!! note

    This part of the project documentation focuses on an **understanding-oriented** approach. You'll get a chance to read about the background of the project, as well as reasoning about how it was implemented.

- Give context and background on your library
- Explain why you created it
- Provide multiple examples and approaches of how to work with it
- Help the reader make connections
- Avoid writing instructions or technical descriptions here

``` mermaid
classDiagram
  AnalogCircuit <|-- Statement
  
  Statement <|-- Initialize
  Statement <|-- Evolve
  Statement <|-- Measure
  
  Evolve <|-- AnalogGate
  
  class AnalogCircuit{
    +list[Statement] sequence
  }
  
  class Statement{
    +int sequence
  }
  class Initialize{
    +int sequence
  }
  class Evolve{
    +int sequence
  }
  class Measure{
    can this be anything
  }
  
  class AnalogGate{
    +list[int] qreg
    +list[int] qmode
  }
```