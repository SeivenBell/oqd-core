from quantumion.compiler.visitor import Visitor, Transform
from quantumion.interface.analog.circuit import AnalogCircuit

########################################################################################


class AnalogCircuitVisitor(Visitor):
    pass


class AnalogCircuitTransform(Transform):
    pass


class AnalogCircuitIonsAnalysis(AnalogCircuitVisitor):
    def __init__(self):
        self.ions = 0

    def visit_AnalogCircuit(self, model: AnalogCircuit) -> None:
        assert isinstance(model, AnalogCircuit)
        self.ions = model.n_qreg


########################################################################################
