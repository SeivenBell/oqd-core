from quantumion.compiler.visitor import Visitor, Transform
from quantumion.atomic.schedule import Register

########################################################################################


class AtomicProgramVisitor(Visitor):
    pass


class AtomicProgramTransform(Transform):
    pass


class CountIonsAnalysis(AtomicProgramVisitor):
    def __init__(self):
        self.ions = 0

    def reset(self):
        self.ions = 0

    def visit_Register(self, model: Register) -> None:
        assert isinstance(model, Register)
        self.ions += len(model.configuration)


########################################################################################
