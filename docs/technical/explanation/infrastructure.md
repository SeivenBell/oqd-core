We are using the Visitor patter, but have separated the logic (`Rule`) and IR Traversal (`Walk`) for more flexibility. 

## RewriteRules

Rewrite Rules in compilers are basically used to match and then transform an expression. For example, similifying an expression like `2 * (1 + 3)` to `2 * 1 + 2 * 3` is a form of rewriting the expression. here we demonstrate rewriting with the simple example shown below:
$$
X@(Y*I)\rightarrow X@Y
$$
This rewrite modified the AST as shown below. This Rule is an example of [`PauliAlgebra`][midstack.compiler.analog.rewrite.canonicalize.PauliAlgebra]. Here we basically rewrite the right hand side of the `OperatorKron`.

=== "Original Graph"
    ```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element2("PauliI"):::Pauli
    element3("OperatorMul"):::OperatorMul
    element3 --> element1 & element2
    element4("OperatorKron"):::OperatorKron
    element4 --> element0 & element3
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#700000,stroke-width:3px
    classDef OperatorAdd stroke:#3495BD,stroke-width:3px
    classDef OperatorScalarMul stroke:#500000,stroke-width:3px
    classDef OperatorKron stroke:#A452B3,stroke-width:3px
    classDef OperatorMul stroke:300000,stroke-width:3px
    classDef MathExpr stroke:#100000,stroke-width:3px
    ```

=== "Transformed Graph after Rewrite"
    ```mermaid
    graph TD
    element0("PauliX"):::Pauli
    element1("PauliY"):::Pauli
    element4("OperatorKron"):::OperatorKron
    element4 --> element0 & element1
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#700000,stroke-width:3px
    classDef OperatorAdd stroke:#3495BD,stroke-width:3px
    classDef OperatorScalarMul stroke:#500000,stroke-width:3px
    classDef OperatorKron stroke:#A452B3,stroke-width:3px
    classDef OperatorMul stroke:300000,stroke-width:3px
    classDef MathExpr stroke:#100000,stroke-width:3px

    ```

Note that `RewriteRule` does not traverse through the graph. To traverse a graph we use `Walk`.

## Walk
Walks are just the different ways of traversing graphs. Example for this case. We have several types of `Walk`. I will show the different types using the following the Tree.

```mermaid
    graph TD
    element0("B0"):::OperatorMul
    element1("C2"):::Pauli
    element2("C3"):::Pauli
    element3("B1"):::OperatorMul
    element3 --> element1 & element2
    element4("A0"):::OperatorKron
    element4 --> element0 & element3
    element5("C0"):::Pauli
		element6("C1"):::Pauli
    element0 --> element5 & element6
    classDef Pauli stroke:#800000,stroke-width:3px
    classDef Ladder stroke:#700000,stroke-width:3px
    classDef OperatorAdd stroke:#3495BD,stroke-width:3px
    classDef OperatorScalarMul stroke:#500000,stroke-width:3px
    classDef OperatorKron stroke:#A452B3,stroke-width:3px
    classDef OperatorMul stroke:300000,stroke-width:3px
    classDef MathExpr stroke:#100000,stroke-width:3px

```
=== "Pre"
    === "Regular"
        $$ A0\rightarrow B0 \rightarrow C0 \rightarrow C1  \rightarrow B1 \rightarrow C2 \rightarrow C3 $$
    === "Reverse"
        $$ A0\rightarrow B1 \rightarrow C3 \rightarrow C2  \rightarrow B0 \rightarrow C1 \rightarrow C0 $$
=== "Post"
    === "Regular"
        $$ C0\rightarrow C1 \rightarrow B0 \rightarrow C2 \rightarrow C3 \rightarrow B1 \rightarrow A0 $$
    === "Reverse"
        $$ C3\rightarrow C2 \rightarrow B1 \rightarrow C1 \rightarrow C0 \rightarrow B0 \rightarrow A0 $$
=== "In"
    === "Regular"
        $$ C0\rightarrow B0 \rightarrow C1 \rightarrow A0 \rightarrow C2 \rightarrow B1 \rightarrow C3 $$
    === "Reverse"
        $$ C3\rightarrow B1 \rightarrow C2 \rightarrow A0 \rightarrow C1 \rightarrow B0 \rightarrow C0 $$
=== "Level"
    === "Regular"
        $$ A0\rightarrow B0 \rightarrow B1 \rightarrow C0 \rightarrow C1 \rightarrow C2 \rightarrow C3 $$
    === "Reverse"
        $$ A0\rightarrow B1 \rightarrow B0 \rightarrow C3 \rightarrow C2 \rightarrow C1 \rightarrow C0 $$
