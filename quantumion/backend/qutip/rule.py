from quantumion.interface.analog.operator import *
from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.analog.operations import *
from quantumion.backend.task import TaskArgsAnalog, TaskResultAnalog, ComplexFloat
from quantumion.compiler.math.base import VerbosePrintMathExpr, EvaluateMathExpr
from quantumion.backend.qutip.interface import (
    QutipExperiment,
    QutipOperation,
    TaskArgsQutip,
    QutipExpectation,
)
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from typing import Any, Union, List, Tuple, Literal, Dict
import qutip as qt
from pydantic import BaseModel, ConfigDict
from quantumion.compilerv2.walk import *
from quantumion.compilerv2.rule import *
from rich import print as pprint
import numpy as np
from pydantic.types import NonNegativeInt
import itertools
import time
import ast
# define the target and then build a new model based on the target
"""
- Source: Analog
- Target: Qutip
"""

def entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode):
    rho = qt.ptrace(
        psi,
        qreg
        + [n_qreg + m for m in qmode],  # canonical index for each local Hilbert space
    )
    return qt.entropy_vn(rho)

class QutipExperimentInterpreter(ConversionRule):

    def map_QutipExpectation(self, model: QutipExpectation, operands):
        for idx, operator in enumerate(model.operator):
            coefficient = operator[1].accept(EvaluateMathExpr()) # using visitor
            op_exp = (
                coefficient * operator[0]
                if idx == 0
                else op_exp + coefficient * operator[0]
            )
        pprint("qutip exp is {}".format(op_exp))
        return lambda t, psi: qt.expect(op_exp, psi)

    def map_EntanglementEntropyVN(self, model: EntanglementEntropyVN, operands):
        raise NotImplementedError
        ## same problem as before
        # return lambda t, psi: entanglement_entropy_vn(
        #     t, psi, model.qreg, model.qmode, self.n_qreg, self.n_qmode
        # )
    
    def map_TaskArgsQutip(self, model: TaskArgsQutip, operands):
        return operands

    def map_QutipExperiment(self, model: QutipExperiment, operands) -> TaskResultAnalog:
        pprint("map_QutipExperiment operands are {}".format(operands))
        dims = model.n_qreg * [2] + model.n_qmode * [model.args.fock_cutoff]
        self.n_qreg = model.n_qreg
        self.n_qmode = model.n_qmode
        initial_state = qt.tensor([qt.basis(d, 0) for d in dims])

        qutip_metrics = operands['args']['metrics']

        current_state = initial_state

        start_time = time.time()

        results = []
        for instruction in model.instructions:
            results.append(self._QutipOperation(model=instruction, 
                                           dt = model.args.dt, 
                                           current_state=current_state, 
                                           qutip_metrics=qutip_metrics))
            current_state = results[-1].final_state

        time_taken = time.time() - start_time

        times = []
        metrics = {key: np.empty(0) for key in qutip_metrics.keys()}
        for idx, result in enumerate(results):
            result_times = result.times[1:] if idx != 0 else result.times
            duration_tracker = (
                model.instructions[idx - 1].duration + duration_tracker
                if idx != 0
                else 0
            )
            times = np.hstack(
                [
                    times,
                    (
                        [t + duration_tracker for t in result_times]
                        if idx != 0
                        else result_times
                    ),
                ]
            )

            for i, key in enumerate(metrics.keys()):
                result_expect = result.expect[i][1:] if idx != 0 else result.expect[i]
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
            counts = {
                bitstring: bitstrings.count(bitstring) for bitstring in bitstrings
            }

        return TaskResultAnalog(
            times=times,
            metrics=metrics,
            state=list(
                results[-1].final_state.full().squeeze(),
            ),
            counts=counts,
            runtime=time_taken,
        )

    def _QutipOperation(self, model: QutipOperation, dt, current_state, qutip_metrics): # remove
        duration = model.duration
        tspan = np.linspace(
            0, duration, round(duration / dt)
        )  # create time vector
        qutip_hamiltonian = []
        for op, coeff in model.hamiltonian:
            qutip_hamiltonian.append([op, coeff.accept(VerbosePrintMathExpr())]) # using visitor
        result_qobj = qt.sesolve(
            qutip_hamiltonian,
            current_state,
            tspan,
            e_ops=qutip_metrics,
            options={"store_states": True},
        )

        self._current_state = result_qobj.final_state

        return result_qobj

class QutipBackendTransformer(ConversionRule):

    def map_AnalogCircuit(self, model: AnalogCircuit, operands):
        # pprint("operands in curciot is {}\n".format(operands))
        return operands['sequence']

    def map_Task(self, model: Task, operands):
        return QutipExperiment(
            instructions=operands['program'],
            n_qreg=model.program.n_qreg,
            n_qmode=model.program.n_qmode, ## maybe put them inside operands and output this in AC instrad of accessing the program object here. seems more rigorous
            args=operands['args'],
        )

    def map_TaskArgsAnalog(self, model: TaskArgsAnalog, operands):
        pprint("mode metricsl: {} amd op is {}\n".format(model, operands))
        return TaskArgsQutip(
            layer=model.layer,
            n_shots=model.n_shots,
            fock_cutoff=model.fock_cutoff,
            dt=model.dt,
            metrics = operands['metrics'],
            # metrics=self(model.metrics),
        )

    def map_Expectation(self, model: Expectation, operands):
        return QutipExpectation(operator=operands['operator'])
        # return QutipExpectation(operator=self(model=model.operator))


    def map_Evolve(self, model: Evolve, operands):
        return QutipOperation(
            # hamiltonian=self(model.gate), duration=model.duration
            hamiltonian=operands['gate'], duration=model.duration
        )

    def map_AnalogGate(self, model: AnalogGate, operands):
        # pprint("operands in analog gate is {}\n".format(operands))
        # return self(model.hamiltonian)
        return operands['hamiltonian']

    def map_OperatorAdd(self, model: OperatorAdd, operands):
        # pprint("operands in adddd is {}\n".format(operands))
        op = operands['op1']#self(model.op1)
        op.append(operands['op2'][0])
        return op

    def map_OperatorScalarMul(self, model: OperatorScalarMul, operands):
        # return [(self(model.op), model.expr)]
        return [(operands['op'], model.expr)]

    def map_PauliI(self, model: PauliI, operands) -> qt.Qobj:
        return qt.qeye(2)

    def map_PauliX(self, model: PauliX, operands) -> qt.Qobj:
        pprint("operands in model {} is {}\n".format(model, operands))
        return qt.sigmax()

    def map_PauliY(self, model: PauliY, operands) -> qt.Qobj:
        return qt.sigmay()

    def map_PauliZ(self, model: PauliZ, operands) -> qt.Qobj:
        return qt.sigmaz()

    def map_Identity(self, model: Identity, operands) -> qt.Qobj:
        raise NotImplementedError
        #return qt.qeye(model.fock_cutoff)

    def map_Creation(self, model: Creation, operands) -> qt.Qobj:
        raise NotImplementedError
        #return qt.create(model.fock_cutoff)

    def map_Annihilation(self, model: Annihilation, operands) -> qt.Qobj:
        raise NotImplementedError
        #return qt.destroy(model.fock_cutoff)

    def map_OperatorMul(self, model: OperatorMul, operands) -> qt.Qobj:
        return operands['op1'] * operands['op2']

    def map_OperatorKron(self, model: OperatorKron, operands) -> qt.Qobj:
        return qt.tensor(operands['op1'], operands['op2'])


if __name__ == '__main__':
    from quantumion.compiler.analog.base import *
    X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()
    # op = X@Y@(A*C*A) + X@Z + Z + Z@I@C
    # out = PreWithNonVisitableOutput(TermIndex())(op)
    # pprint("lst out is {}".format(out))
    ac = AnalogCircuit()
    ac.evolve(gate=AnalogGate(hamiltonian=1*(X@X)+ 1*(Y@Y) + 1*(I@I) + 3*(Z@I)), duration=1)
    ac.n_qreg = 2
    ac.n_qmode = 0
    args = TaskArgsAnalog(n_shots=100, metrics={
        'exp' : Expectation(operator=2*(I@Y) + 3*(I@I)),
    })

    task = Task(
        program=ac,
        args = args
    )
    out = PostConversion(QutipBackendTransformer())(task) # 'Qobj' object has no attribute 'keys' for post
        # pprint(Pre(QutipBackendTransformer())(ac)) # causes AttributeError: 'list' object has no attribute 'model_fields'
    pprint(PostConversion(QutipExperimentInterpreter())(out))

