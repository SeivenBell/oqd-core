from quantumion.interface.analog.operator import *
from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.analog.operations import *
from quantumion.backend.task import TaskArgsAnalog, TaskResultAnalog, ComplexFloat
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
    ac.n_qreg = 100
    ac.n_qmode = 20
    args = TaskArgsAnalog(n_shots=100, metrics={
        'exp' : Expectation(operator=2*(I@Y) + 3*(I@I)),
    })

    task = Task(
        program=ac,
        args = args
    )
    pprint(PostConversion(QutipBackendTransformer())(task)) # 'Qobj' object has no attribute 'keys' for post
        # pprint(Pre(QutipBackendTransformer())(ac)) # causes AttributeError: 'list' object has no attribute 'model_fields'

