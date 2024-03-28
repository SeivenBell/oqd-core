from quantumion.compiler.analog.base import AnalogInterfaceTransformer, AnalogCircuitTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.base import VisitableBaseModel
from quantumion.compiler.math import VerbosePrintMathExpr
from quantumion.interface.analog.operations import *
from quantumion.backend.task import TaskArgsAnalog, TaskResultAnalog, ComplexFloat
from quantumion.backend.analog.python.qutip_interface import QutipExperiment, QutipOperation
from quantumion.backend.metric import *
from typing import Any, Union, List, Tuple, Literal, Dict
import qutip as qt
from pydantic import BaseModel, ConfigDict
from rich import print as pprint
import numpy as np
from pydantic.types import NonNegativeInt
import itertools

__all__ = [
    "QutipBackendTransformer",
    "QutipExperimentEvolve",
]


class QutipExperimentMeasure(AnalogInterfaceTransformer):
    def __init__(self, state):
        super().__init__()
        self._state = state

    def visit_QutipExperiment(self, model: QutipExperiment):
        if model.args.n_shots is None:
            return {}
        probs = np.power(np.abs(self._state.full()), 2).squeeze()
        n_shots = model.args.n_shots
        inds = np.random.choice(len(probs), size=n_shots, p=probs)
        opts = model.n_qreg * [[0, 1]] + model.n_qmode * [
            list(range(model.args.fock_cutoff))
        ]
        bases = list(itertools.product(*opts))
        shots = np.array([bases[ind] for ind in inds])
        bitstrings = ["".join(map(str, shot)) for shot in shots]
        return {bitstring: bitstrings.count(bitstring) for bitstring in bitstrings}

class QutipExperimentEvolve(AnalogInterfaceTransformer):
    def __init__(self):
        super().__init__()
        self._current_state = None

    def visit_QutipExperiment(self, model: QutipExperiment) -> TaskResultAnalog:
        dims = model.n_qreg * [2] + model.n_qmode * [model.args.fock_cutoff]
        initial_state = qt.tensor([qt.basis(d, 0) for d in dims])

        self._qutip_metrics = model.args.accept(MetricsToQutipObjects(
            n_qreg = model.n_qreg,
            n_qmode = model.n_qmode,
        ))

        self._current_state = initial_state

        self._dt = model.args.dt

        results = self.visit(model.instructions)

        times = []
        metrics = {key: np.empty(0) for key in self._qutip_metrics.keys()}
        for idx, result in enumerate(results):
            result_times = result.times[1:] if idx != 0 else result.times
            times = np.hstack([times, result_times + model.instructions[idx-1].duration if idx != 0 else result_times])

            for key in metrics.keys():
                result_expect = result.expect[key][1:] if idx != 0 else result.expect[key]
                metrics.update({key: np.hstack([metrics[key], result_expect])})

        return TaskResultAnalog(
            times = times,
            metrics = metrics,
            state = list(map(ComplexFloat.cast_from_np_complex128, results[-1].final_state.full().squeeze())), #results[-1].final_state.full(), # convert to complexfloat
            counts = model.accept(
                visitor = QutipExperimentMeasure(state=results[-1].final_state)
            )
        )

    def visit_QutipOperation(self, model: QutipOperation):
        duration = model.duration
        tspan = np.linspace(
            0, duration, round(duration / self._dt)
        )  # create time vector    

        options = qt.solver.Options(store_final_state=True)

        result_qobj = qt.sesolve(
            model.hamiltonian, self._current_state, tspan, e_ops= self._qutip_metrics, options=options
        )

        self._current_state = result_qobj.final_state

        return result_qobj


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

    
    def visit_TaskArgsAnalog(self, model: TaskArgsAnalog) -> dict:
        self.fock_cutoff = model.fock_cutoff
        return self.visit(model.metrics)

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
            args=self.args
        )
    
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