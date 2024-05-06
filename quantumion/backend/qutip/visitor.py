from quantumion.compiler.analog.base import (
    AnalogInterfaceTransformer,
    AnalogCircuitTransformer,
)
from quantumion.interface.analog.operator import *
from quantumion.interface.base import VisitableBaseModel
from quantumion.compiler.math import VerbosePrintMathExpr, SerializeMathExpr
from quantumion.interface.analog.operations import *
from quantumion.backend.task import TaskArgsAnalog, TaskResultAnalog, ComplexFloat
from quantumion.backend.qutip.interface import QutipExperiment, QutipOperation, TaskArgsQutip, QutipExpectation
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from typing import Any, Union, List, Tuple, Literal, Dict
import qutip as qt
from pydantic import BaseModel, ConfigDict
from rich import print as pprint
import numpy as np
from pydantic.types import NonNegativeInt
import itertools
import time
import ast

__all__ = [
    "QutipBackendTransformer",
    "QutipExperimentEvolve",
]


class QutipExperimentEvolve(AnalogInterfaceTransformer):
    def __init__(self):
        super().__init__()
        self._current_state = None

    def visit_QutipExpectation(self, model: QutipExpectation):
        for idx, operator in enumerate(model.operator):
            coefficient = operator[1].accept(SerializeMathExpr())
            op_exp = coefficient * operator[0] if idx == 0 else op_exp + coefficient * operator[0]
        return lambda t, psi: qt.expect(
            op_exp, psi
        )

    def visit_EntanglementEntropyVN(self, model: EntanglementEntropyVN):
        return lambda t, psi: entanglement_entropy_vn(
            t, psi, model.qreg, model.qmode, self.n_qreg, self.n_qmode
        )

    def visit_QutipExperiment(self, model: QutipExperiment) -> TaskResultAnalog:
        dims = model.n_qreg * [2] + model.n_qmode * [model.args.fock_cutoff]
        self.n_qreg = model.n_qreg
        self.n_qmode = model.n_qmode
        initial_state = qt.tensor([qt.basis(d, 0) for d in dims])

        self._qutip_metrics = self.visit(model.args.metrics)

        self._current_state = initial_state

        self._dt = model.args.dt

        start_time = time.time()
        results = self.visit(model.instructions)
        time_taken = time.time() - start_time

        times = []
        metrics = {key: np.empty(0) for key in self._qutip_metrics.keys()}
        for idx, result in enumerate(results):
            result_times = result.times[1:] if idx != 0 else result.times
            duration_tracker = (
                model.instructions[idx - 1].duration + duration_tracker
                if idx != 0
                else 0
            )
            times = np.hstack(
                [times, [t + duration_tracker for t in result_times] if idx != 0 else result_times]
            )

            for i, key in enumerate(metrics.keys()):
                result_expect = (
                    result.expect[i][1:] if idx != 0 else result.expect[i]
                )
                metrics.update({key: np.hstack([metrics[key], result_expect])})

        if model.args.n_shots is None:
            counts = {}
        else:
            probs = np.power(np.abs(results[-1].final_state.full()), 2).squeeze()
            n_shots = model.args.n_shots
            inds = np.random.choice(len(probs), size=n_shots, p=probs)
            opts = model.n_qreg * [[0, 1]] + model.n_qmode * [
                list(range(model.args.fock_cutoff))
            ]
            bases = list(itertools.product(*opts))
            shots = np.array([bases[ind] for ind in inds])
            bitstrings = ["".join(map(str, shot)) for shot in shots]
            counts = {bitstring: bitstrings.count(bitstring) for bitstring in bitstrings}

        return TaskResultAnalog(
            times=times,
            metrics=metrics,
            state=list(
                results[-1].final_state.full().squeeze(),
            ),
            counts = counts,
            runtime=time_taken,
        )

    def visit_QutipOperation(self, model: QutipOperation):
        duration = model.duration
        tspan = np.linspace(
            0, duration, round(duration / self._dt)
        )  # create time vector
        qutip_hamiltonian = []
        for op, coeff in model.hamiltonian:
            qutip_hamiltonian.append([op, coeff.accept(VerbosePrintMathExpr())])
        result_qobj = qt.sesolve(
            qutip_hamiltonian,
            self._current_state,
            tspan,
            e_ops=self._qutip_metrics,
            options={"store_states": True},
        )

        self._current_state = result_qobj.final_state

        return result_qobj


def entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode):
    rho = qt.ptrace(
        psi,
        qreg
        + [n_qreg + m for m in qmode],  # canonical index for each local Hilbert space
    )
    return qt.entropy_vn(rho)


class QutipBackendTransformer(AnalogInterfaceTransformer):
    """convert task to QutipObj without running (maybe use visitor?)
    Basically compiles down to qutip object using transformers.
    """

    def visit_Task(self, model: Task):
        self.args = model.args # Without args we cannot define a QutipExperiment
        return self.visit(model.program)

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        return QutipExperiment(
            instructions=self.visit(model.sequence),
            n_qreg=model.n_qreg,
            n_qmode=model.n_qmode,
            args=self.visit(self.args),
        )
    
    def visit_TaskArgsAnalog(self, model: TaskArgsAnalog):
        return TaskArgsQutip(
            layer=model.layer,
            n_shots=model.n_shots,
            fock_cutoff=model.fock_cutoff,
            dt = model.dt,
            metrics=self.visit(model.metrics)
        )
    
    def visit_Expectation(self, model: Expectation):
        return QutipExpectation(operator=self.visit(model=model.operator))

    def visit_Evolve(self, model: Evolve):
        return QutipOperation(
            hamiltonian=self.visit(model.gate), duration=model.duration
        )

    def visit_AnalogGate(self, model: AnalogGate):
        return self.visit(model.hamiltonian)

    def visit_OperatorAdd(self, model: OperatorAdd):
        op = self.visit(model.op1)
        op.append(self.visit(model.op2)[0])
        return op

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        # pprint("scalar mul is {}".format(model))
        return [
            (
                self.visit(model.op),
                model.expr
            )
        ]

    def visit_PauliI(self, model: PauliI) -> qt.Qobj:
        return qt.qeye(2)

    def visit_PauliX(self, model: PauliX) -> qt.Qobj:
        return qt.sigmax()

    def visit_PauliY(self, model: PauliY) -> qt.Qobj:
        return qt.sigmay()

    def visit_PauliZ(self, model: PauliZ) -> qt.Qobj:
        return qt.sigmaz()

    def visit_Identity(self, model: Identity) -> qt.Qobj:
        return qt.qeye(self.args.fock_cutoff)

    def visit_Creation(self, model: Creation) -> qt.Qobj:
        return qt.create(self.args.fock_cutoff)

    def visit_Annihilation(self, model: Annihilation) -> qt.Qobj:
        return qt.destroy(self.fock_cutoff)

    def visit_OperatorMul(self, model: OperatorMul) -> qt.Qobj:
        return self.visit(model.op1) * self.visit(model.op2)

    def visit_OperatorKron(self, model: OperatorKron) -> qt.Qobj:
        return qt.tensor(self.visit(model.op1), self.visit(model.op2))

    # def visit_OperatorAdd(self, model: OperatorAdd) -> qt.Qobj:
    #     return self.visit(model.op1) + self.visit(model.op2)

    # def visit_OperatorScalarMul(self, model: OperatorScalarMul) -> qt.Qobj:
    #     return model.expr.value * self.visit(model.op)