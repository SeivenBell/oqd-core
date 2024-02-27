# Units

Looking through [unyt](https://unyt.readthedocs.io/en/stable/usage.html), there are many intricacies in implementing units.

## Function handling

### Exponentials and Logarithms

/// admonition | Example
$\exp(1 \ \mathrm{(cm)})$ <br/>
$\log (1 \ \mathrm{(cm)})$
///


### Trigonometry

Should we assign a unit to angles?

/// admonition | Example
$\sin(1 \  (rad))$
///

### Power
Expressions with varying units?

/// admonition | Example
$1 (\mathrm{cm}) ** \ 2$ <br/>
$1 (\mathrm{cm}) ** \ ({w (\mathrm{Hz}) * t (\mathrm{s})})$
///

## Performace

Under performance considerations, units should be implemented in the interfaces and not within computational blocks.

In our case, this means we may want to compile out units in the intermediate representation (IR).


## Implementation

=== "Global"
    Global implementation of units tags the abstract syntax tree (AST) of mathematical expressions with a unit.

    - [x] 1 (cm)
    - [x] $t$ (s)
        - $t$ is substituted with a pure number (no units)
    - [x] $\sin(w*t)$ (cm)
    - [x] 1 (Hz) * 1 (s)
        - converted to  1 (unitless) in the AST
    - [ ] Verification of unit compatibility
        - consider $\sin(w*t)$ $\rightarrow$ $w*t$ is assumed dimensionless
    - [x] Any expression can have any units:
        - e.g. $t^7$ (cm)

=== "Local"
    Local implementation of units deeply integrates units into the abstract syntax tree (AST) of mathematical expressions.

    - [x] 1 (cm)
    - [ ] $t$ (s)
        - Does not make sense to assign variable $t$ a concrete unit
    - [x] $t$ [Time]
        - $t$ has to be substituted with a value and a time unit, e.g. 1 (s), 2 (min), 3(hours)
    - [ ] $\sin(w*t)$ (cm)
        - Functions are unitless
        - Units need to be assigned with multiplication: 1 (cm) * $\sin(w*t)$ 
    - [x] 1 (Hz) * 1 (s)
        - kept in this form in the AST
    - [x] Verification of unit compatibility
        - consider $\sin(w*t)$ $\rightarrow$ $w \ [\mathrm{Time}^{-1}] * t \ [\mathrm{Time}]$ can be verified to be dimensionless
    - [x] Expressions must have the appropriate coefficients
        - e.g. $t^7$ (cm) $\rightarrow$ $1 \left( \mathrm{cm}/\mathrm{s}^7 \right) * t^7 \left[ \mathrm{Time}^7 \right]$

### AST
=== "Global"
    ```mermaid
    flowchart TB

    unitful[[Unitful]]

    add["+ (Math)"]

    num1(1)
    var2(a)

    unit(cm)

    unitful --> add & unit
    add --> num1 & var2
    ```
=== "Local"
    ```mermaid
    flowchart TB

    add["+ (Unitful)"]

    num1(1)
    var2(a)

    unitful1[[Unitful]]

    unitful2[[Unitful]]

    unit1(cm)
    dimension2(length)

    add --> unitful1 & unitful2

    unitful1 --> num1 & unit1
    unitful2 --> var2 & dimension2

    ```