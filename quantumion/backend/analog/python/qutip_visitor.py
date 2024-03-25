from quantumion.compiler.analog.base import AnalogInterfaceTransformer, AnalogCircuitTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.base import VisitableBaseModel
from quantumion.compiler.math import VerbosePrintMathExpr
from quantumion.interface.analog.operations import *
from typing import Any, Union, List, Tuple, Literal, Dict
import qutip as qt
from pydantic import BaseModel, ConfigDict
from rich import print as pprint
import numpy as np
from pydantic.types import NonNegativeInt
import itertools

__all__ = [
    "QutipBackendTransformer",
    "QutipConvertTransformer",
    "QutipExperimentTransform",
    "MetricsToQutipObjects",
    "TaskArgsAnalog",
    "Expectation",
    "EntanglementEntropyVN",
]

##############################################################
class Expectation(VisitableBaseModel):
    operator: Operator

class EntanglementEntropyVN(VisitableBaseModel):
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


class EntanglementEntropyReyni(VisitableBaseModel):
    alpha: NonNegativeInt = 1
    qreg: List[NonNegativeInt] = []
    qmode: List[NonNegativeInt] = []


Metric = Union[EntanglementEntropyVN, EntanglementEntropyReyni, Expectation]
##############################################################
class TaskArgsAnalog(VisitableBaseModel):
    layer: Literal["analog"] = "analog"
    n_shots: int = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Metric] = {}

class QutipOperation(VisitableBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    hamiltonian: list[Tuple[qt.Qobj, str]] #list[qt.qobj.Qobj] # good for ensuring correct type # for consistency we will always define this way
    duration: float
    
class QutipExperiment(VisitableBaseModel):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    # initial_state: Union[qt.Qobj, None] = None
    instructions: list[QutipOperation]
    n_qreg: NonNegativeInt
    n_qmode: NonNegativeInt
    args: TaskArgsAnalog
    ## should have everything to define a qutip exp


class QutipConvertTransformer(AnalogCircuitTransformer):
    def __init__(self, fock_cutoff):
        super().__init__()
        self.fock_cutoff = fock_cutoff

    def visit_PauliI(self, model: PauliI) -> qt.Qobj:
        return qt.qeye(2)

    def visit_PauliX(self, model: PauliX) -> qt.Qobj:
        return qt.sigmax()
    
    def visit_PauliY(self, model: PauliY) -> qt.Qobj:
        return qt.sigmay()

    def visit_PauliZ(self, model: PauliZ) -> qt.Qobj:
        return qt.sigmaz()
    
    def visit_Identity(self, model: Identity) -> qt.Qobj:
        return qt.qeye(self.fock_cutoff)

    def visit_Creation(self, model: Creation) -> qt.Qobj:
        return qt.create(self.fock_cutoff)
    
    def visit_Annihilation(self, model: Annihilation) -> qt.Qobj:
        return qt.destroy(self.fock_cutoff)

    def visit_OperatorMul(self, model: OperatorMul) -> qt.Qobj:
        return self.visit(model.op1) * self.visit(model.op2)
    
    def visit_OperatorKron(self, model: OperatorKron) -> qt.Qobj:
        return qt.tensor(self.visit(model.op1), self.visit(model.op2))

    def visit_OperatorAdd(self, model: OperatorAdd) -> qt.Qobj:
        return self.visit(model.op1) + self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul) -> qt.Qobj:
        return  model.expr.value * self.visit(model.op)

def entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode):
    rho = qt.ptrace(
        psi,
        qreg
        + [n_qreg + m for m in qmode],  # canonical index for each local Hilbert space
    )
    return qt.entropy_vn(rho)

class MetricsToQutipObjects(AnalogInterfaceTransformer): # task analog to taskqutipanalog
    """
    Transforms TaskArgsAnalog such that metrics converted to qutip  lambda objects
    """
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self.n_qreg = n_qreg
        self.n_qmode = n_qmode
        
    def _visit(self, model: Any):
        if isinstance(model, dict):
            return {
                key: self.visit(metric)
                for (key, metric) in model.items()
            }
        else:
            super(self.__class__, self)._visit(model)

    
    def visit_TaskArgsAnalog(self, model: TaskArgsAnalog):
        model.metrics = self.visit(model.metrics)
        self.fock_cutoff = model.fock_cutoff
        return model

    def visit_EntanglementEntropyVN(self, model: EntanglementEntropyVN):
        return lambda t, psi: entanglement_entropy_vn(
                t, psi, model.qreg, model.qmode, self.n_qreg, self.n_qmode
            )
    def visit_Expectation(self, model: Expectation):
        return lambda t, psi: qt.expect(model.operator.accept(QutipConvertTransformer(self.fock_cutoff)), psi) #model.operator.accept(QutipBackendTransformer())

class QutipBackendTransformer(AnalogInterfaceTransformer):
    """convert task to QutipObj without running (maybe use visitor?)
    Basically compiles down to qutip object using transformers.
    """
    def __init__(self, args):
        super().__init__()
        self.args = args

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        return QutipExperiment(
            instructions=self.visit(model.sequence), 
            n_qreg=model.n_qreg, 
            n_qmode = model.n_qmode, 
            args=self.args.accept(MetricsToQutipObjects(
                n_qreg = model.n_qreg, 
                n_qmode = model.n_qmode
        )))
    
    def visit_Evolve(self, model: Evolve):
        return QutipOperation(hamiltonian=self.visit(model.gate), duration=model.duration)

    def visit_AnalogGate(self, model: AnalogGate):
        return self.visit(model.hamiltonian)
    
    def visit_OperatorAdd(self, model: OperatorAdd):        
        op = self.visit(model.op1)
        op.append(self.visit(model.op2)[0])
        return op
    
    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        return [(model.op.accept(QutipConvertTransformer(fock_cutoff=self.args.fock_cutoff)), model.expr.accept(VerbosePrintMathExpr()))]

if __name__ == "__main__":
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()