from quantumion.compiler.visitor import Visitor, Transformer
from quantumion.interface.atomic.register import Register

########################################################################################


class AtomicProgramVisitor(Visitor):
    pass


class AtomicProgramTransformer(Transformer):
    pass


class AtomicProgramIonsAnalysis(AtomicProgramVisitor):
    def __init__(self):
        self.ions = 0

    def reset(self):
        self.ions = 0

    def visit_Register(self, model: Register) -> None:
        assert isinstance(model, Register)
        self.ions += len(model.configuration)


########################################################################################
