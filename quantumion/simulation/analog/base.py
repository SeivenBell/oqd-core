from quantumion.compiler.visitor import * ## maybe put visitor outside of compiler?

__all__ = [
    "AnalogInterfaceVisitor",
    "AnalogInterfaceTransformer",
]


class AnalogInterfaceVisitor(Visitor):
    pass


class AnalogInterfaceTransformer(Transformer):
    pass