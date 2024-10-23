Canonicalization is used to remove redundancy in the representation of a program.

Consider the following two Hamiltonians:

$$
H_{1} = X \otimes I + I \otimes X
$$

$$
H_{2} = I \otimes X + X \otimes I
$$

$H_{1}$ is equivalent to $H_{2}$. Hence we convert the operators to a canonical form and the canonical form of the above operator is:

$$
H_{c} = 1\cdot(I \otimes X) + 1\cdot(X \otimes I)
$$

These canonicalization steps (e.g. distribution) are done by implementing a `RewritesRule` with the corresponding logic.

## Canonicalization Rules

### Distribution

[`Distribution`][oqd_core.compiler.analog.rewrite.canonicalize.OperatorDistribute] distributes the multiplication, scalar multiplication and tensor product of operators over the addition of operators.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$X \otimes (Y + Z) \longrightarrow X \otimes Y + X \otimes Z$$

//// tab | Original Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("PauliZ"):::Pauli
    element3("OperatorAdd"):::OperatorAdd
    element3 --> element1 & element2
    element4("OperatorKron"):::OperatorKron
    element4 --> element0 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("OperatorKron"):::OperatorKron
    element2 --> element0 & element1
    element3("PauliX"):::Pauli
    element4("PauliZ"):::Pauli
    element5("OperatorKron"):::OperatorKron
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Gather Math Expression

[`GatherMath`][oqd_core.compiler.analog.rewrite.canonicalize.GatherMathExpr] centralizes the coefficients of the operators by gathering them.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ X \times 3 \times I \longrightarrow 3 \times (X \times I)$$
//// tab | Original Graph

```mermaid
    graph TD
    element0("MathExpr<br/>--------<br/>expr = #quot;3#quot;"):::MathExpr
    element1("PauliX"):::Pauli
    element2("OperatorScalarMul"):::OperatorScalarMul
    element2 --> element0 & element1
    element3("PauliI"):::Pauli
    element4("OperatorMul"):::OperatorMul
    element4 --> element2 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("MathExpr<br/>--------<br/>expr = #quot;3#quot;"):::MathExpr
    element1("PauliX"):::Pauli
    element2("PauliI"):::Pauli
    element3("OperatorMul"):::OperatorMul
    element3 --> element1 & element2
    element4("OperatorScalarMul"):::OperatorScalarMul
    element4 --> element0 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Proper Order

[`ProperOrder`][oqd_core.compiler.analog.rewrite.canonicalize.ProperOrder] takes a chain of OperatorMul or a chain of OperatorAdd and puts the operation order from left to right.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ X \otimes (Y \otimes Z) \longrightarrow (X \otimes Y) \otimes Z $$

//// tab | Original Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("PauliZ"):::Pauli
    element3("OperatorKron"):::OperatorKron
    element3 --> element1 & element2
    element4("OperatorKron"):::OperatorKron
    element4 --> element0 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("OperatorKron"):::OperatorKron
    element2 --> element0 & element1
    element3("PauliZ"):::Pauli
    element4("OperatorKron"):::OperatorKron
    element4 --> element2 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Pauli Algebra

[`PauliAlgebra`][oqd_core.compiler.analog.rewrite.canonicalize.PauliAlgebra] applies the Pauli algebra to simplify the operator.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ X \times Y + I \times I \longrightarrow iZ + I $$
//// tab | Original Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("OperatorMul"):::OperatorMul
    element2 --> element0 & element1
    element3("PauliI"):::Pauli
    element4("PauliI"):::Pauli
    element5("OperatorMul"):::OperatorMul
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("MathExpr<br/>--------<br/>expr = #quot;1j#quot;"):::MathExpr
    element1("PauliZ"):::Pauli
    element2("OperatorScalarMul"):::OperatorScalarMul
    element2 --> element0 & element1
    element3("PauliI"):::Pauli
    element4("OperatorAdd"):::OperatorAdd
    element4 --> element2 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Normal Order

[`NormalOrder`][oqd_core.compiler.analog.rewrite.canonicalize.NormalOrder] puts the ladder operators into normal order.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ C \times A + A \times C \longrightarrow C \times A + C \times A + J$$
//// tab | Original Graph

```mermaid
    graph TD
    element0("Creation"):::Ladder
    element1("Annihilation"):::Ladder
    element2("OperatorMul"):::OperatorMul
    element2 --> element0 & element1
    element3("Annihilation"):::Ladder
    element4("Creation"):::Ladder
    element5("OperatorMul"):::OperatorMul
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("Creation"):::Ladder
    element1("Annihilation"):::Ladder
    element2("OperatorMul"):::OperatorMul
    element2 --> element0 & element1
    element3("Creation"):::Ladder
    element4("Annihilation"):::Ladder
    element5("OperatorMul"):::OperatorMul
    element5 --> element3 & element4
    element6("Identity"):::Ladder
    element7("OperatorAdd"):::OperatorAdd
    element7 --> element5 & element6
    element8("OperatorAdd"):::OperatorAdd
    element8 --> element2 & element7
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Prune Identity

[`PruneIdentity`][oqd_core.compiler.analog.rewrite.canonicalize.PruneIdentity] prunes the unnecessary ladder identities from the graph.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ C\times A \times J\longrightarrow C \times A$$
//// tab | Original Graph

```mermaid
    graph TD
    element0("Creation"):::Ladder
    element1("Annihilation"):::Ladder
    element2("OperatorMul"):::OperatorMul
    element2 --> element0 & element1
    element3("Identity"):::Ladder
    element4("OperatorMul"):::OperatorMul
    element4 --> element2 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("Creation"):::Ladder
    element1("Annihilation"):::Ladder
    element2("OperatorMul"):::OperatorMul
    element2 --> element0 & element1
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Sorted Order

[`SortedOrder`][oqd_core.compiler.analog.rewrite.canonicalize.SortedOrder] sorts the addition terms in operators into a predefined order.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ X \otimes I + I \otimes X \longrightarrow I \otimes X + X \otimes I$$
//// tab | Original Graph

```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliI"):::Pauli
    element2("OperatorKron"):::OperatorKron
    element2 --> element0 & element1
    element3("PauliI"):::Pauli
    element4("PauliX"):::Pauli
    element5("OperatorKron"):::OperatorKron
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
    graph TD
    element0("PauliI"):::Pauli
    element1("PauliX"):::Pauli
    element2("OperatorKron"):::OperatorKron
    element2 --> element0 & element1
    element3("PauliX"):::Pauli
    element4("PauliI"):::Pauli
    element5("OperatorKron"):::OperatorKron
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////
///

### Scale Terms

[`ScaleTerms`][oqd_core.compiler.analog.rewrite.canonicalize.ScaleTerms] introduces scalar multiplication to terms without a coefficient for a more consistent reprensentation.

<!-- prettier-ignore -->
/// admonition | Example
    type: example

$$ I \otimes X + X \otimes I \longrightarrow 1*(I \otimes X) + 1*(X \otimes I)$$
//// tab | Original Graph

```mermaid
    graph TD
    element0("PauliI"):::Pauli
    element1("PauliX"):::Pauli
    element2("OperatorKron"):::OperatorKron
    element2 --> element0 & element1
    element3("PauliX"):::Pauli
    element4("PauliI"):::Pauli
    element5("OperatorKron"):::OperatorKron
    element5 --> element3 & element4
    element6("OperatorAdd"):::OperatorAdd
    element6 --> element2 & element5
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#800000,stroke-width:3px
    classDef OperatorAdd stroke:#800000,stroke-width:3px
    classDef OperatorScalarMul stroke:#800000,stroke-width:3px
    classDef OperatorKron stroke:#800000,stroke-width:3px
    classDef OperatorMul stroke:#800000,stroke-width:3px
    classDef MathExpr stroke:#800000,stroke-width:3px
```

////

//// tab | Transformed Graph

```mermaid
graph TD
element0("MathExpr<br/>--------<br/>expr = #quot;1#quot;"):::MathExpr
element1("PauliI"):::Pauli
element2("PauliX"):::Pauli
element3("OperatorKron"):::OperatorKron
element3 --> element1 & element2
element4("OperatorScalarMul"):::OperatorScalarMul
element4 --> element0 & element3
element5("MathExpr<br/>--------<br/>expr = #quot;1#quot;"):::MathExpr
element6("PauliX"):::Pauli
element7("PauliI"):::Pauli
element8("OperatorKron"):::OperatorKron
element8 --> element6 & element7
element9("OperatorScalarMul"):::OperatorScalarMul
element9 --> element5 & element8
element10("OperatorAdd"):::OperatorAdd
element10 --> element4 & element9
classDef Pauli stroke:#800000,stroke-width:3px
classDef Ladder stroke:#800000,stroke-width:3px
classDef OperatorAdd stroke:#800000,stroke-width:3px
classDef OperatorScalarMul stroke:#800000,stroke-width:3px
classDef OperatorKron stroke:#800000,stroke-width:3px
classDef OperatorMul stroke:#800000,stroke-width:3px
classDef MathExpr stroke:#800000,stroke-width:3px
```

////

///

## Canonicalization Pass

```mermaid
stateDiagram-v2

[*] --> hspace
hspace --> DistributionPass: done
DistributionPass --> properorder: done
properorder --> PauliAlgebraPass: done
PauliAlgebraPass --> gatherpauli: done
gatherpauli --> NormalOrderVerifier: done
NormalOrderVerifier --> NormalOrderPass: fail
NormalOrderPass --> NormalOrderVerifier: done
NormalOrderVerifier --> pruneidentity: pass
pruneidentity --> distribute_subtraction: done
distribute_subtraction --> sortedorder: done
sortedorder --> scaleterms: done
scaleterms --> terminal: done
```

The subgraphs defined above are:
/// tab | DistributionPass

```mermaid
stateDiagram-v2

    [*] --> distribute
    distribute --> gathermathexpr: done
    gathermathexpr --> distribution_verifier: done
    distribution_verifier --> distribute: fail
    distribution_verifier --> terminal: pass
```

///
/// tab | PauliAlgebraPass

```mermaid
stateDiagram-v2

    [*] --> paulialgebra
    paulialgebra --> gathermathexpr: done
    gathermathexpr --> paulialgebra_verifier: done
    paulialgebra_verifier --> paulialgebra: fail
    paulialgebra_verifier --> terminal: pass
```

///
/// tab | NormalOrderPass

```mermaid
stateDiagram-v2

    [*] --> normalorder
    normalorder --> distribute: done
    distribute --> gathermathexpr: done
    gathermathexpr --> properorder: done
    properorder --> normalorder_verifier: done
    normalorder_verifier --> normalorder: fail
    normalorder_verifier --> terminal: pass
```

///
