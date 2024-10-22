## Passes

<!-- prettier-ignore -->
::: core.compiler.analog.passes.canonicalize
    options:
        heading_level: 3
        members: ["analog_operator_canonicalization"]

## Rewrite Rules

<!-- prettier-ignore -->
::: core.compiler.analog.rewrite.canonicalize
    options:
        heading_level: 3
        members: [
            "OperatorDistribute",
            "GatherMathExpr",
            "GatherPauli",
            "PruneIdentity",
            "PauliAlgebra",
            "NormalOrder",
            "ProperOrder",
            "ScaleTerms",
            "SortedOrder",
        ]

## Verification Rules

<!-- prettier-ignore -->
::: core.compiler.analog.verify.canonicalize
    options:
        heading_level: 3
        members: [
            "CanVerPauliAlgebra",
            "CanVerGatherMathExpr",
            "CanVerOperatorDistribute",
            "CanVerProperOrder",
            "CanVerPruneIdentity",
            "CanVerGatherPauli",
            "CanVerNormalOrder",
            "CanVerSortedOrder",
            "CanVerScaleTerm",
        ]
