The math interface is utilized to specify arbitrary profiles for operands of the instructions in other interfaces.

The abstract syntax tree of the math interface is implemented by [`MathExpr`][oqd_core.interface.math.MathExpr].

Consider the following math expression:

$$
10 \sin^2(\omega t + \phi)
$$

The corresponding [`MathExpr`][oqd_core.interface.math.MathExpr] has the following structure:

```mermaid
    graph TD
    element0("10")
    element1("$$\omega$$")
    element2("$$t$$")
    element3("$$\phi$$")
    element9("2")

    element4("*")
    element5("+")
    element6("sin")
    element7("*")
    element8("^")

    element7 --> element0 & element8
    element8 --> element6
    element8 -- exponent --> element9
    element6 --> element5
    element5 --> element4 & element3
    element4 --> element1 & element2
```

## Terminals

The terminals of the math interface consist of:

/// tab | `MathNum`
[`MathNum`][oqd_core.interface.math.MathNum] represents a number.

<!-- prettier-ignore -->
/// admonition | Note
    type: note
Numbers are considered to belong to the real numbers, i.e. they can be positive or negative floats.
///
///

/// tab | `MathImag`
[`MathImag`][oqd_core.interface.math.MathImag] represents the imaginary unit.
///

/// tab | `MathVar`
[`MathVar`][oqd_core.interface.math.MathVar] represents a protected named variable to be substituted during compile time or runtime.
///

## Operators

The compatible operators for the math interface consist of:

/// tab | `MathAdd`

//// html | div
![](https://img.shields.io/badge/binary-blue)
////

[`MathAdd`][oqd_core.interface.math.MathAdd] represents an addition of two expressions.
///

/// tab | `MathMul`

//// html | div
![](https://img.shields.io/badge/binary-blue)
////

[`MathMul`][oqd_core.interface.math.MathMul] represents an multiplication of two expressions.
///

/// tab | `MathPow`

//// html | div
![](https://img.shields.io/badge/binary-blue)
////

[`MathPow`][oqd_core.interface.math.MathPow] represents an exponentiation of an expression with the other expression.
///

/// tab | `MathSub`

//// html | div
![](https://img.shields.io/badge/binary-blue)
////

[`MathSub`][oqd_core.interface.math.MathSub] represents an subtraction of two expressions.
///

/// tab | `MathDiv`

//// html | div
![](https://img.shields.io/badge/binary-blue)
////

[`MathDiv`][oqd_core.interface.math.MathDiv] represents an division of two expressions.
///

/// tab | `MathFunc`

//// html | div
![](https://img.shields.io/badge/unary-red)
////

[`MathFunc`][oqd_core.interface.math.MathFunc] represents the application of a named function on an expression.

The compatible named functions include:

- trigonometric (`sin`, `cos`, `tan`)
- hyperbolic trigonometric (`sinh`, `cosh`, `tanh`)
- exponential (`exp`)
- logarithm (`log`)

///
