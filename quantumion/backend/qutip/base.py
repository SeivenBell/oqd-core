from typing import Optional

########################################################################################

from quantumion.backend.qutip.rule import (
    QutipBackendTransformer,
    QutipExperimentInterpreter,
)
from quantumion.backend.base import BackendBase
from quantumion.backend.qutip.interface import QutipExperiment

from quantumion.backend.task import Task

from quantumion.compiler.flow import *
from quantumion.compiler.analog.verification_flow import VerificationFlow

########################################################################################
__all__ = [
    "QutipBackend",
]

    
from quantumion.compilerv2.analog.assign import AssignAnalogIRDim
from quantumion.compilerv2.walk import Post, PostConversion
from quantumion.compilerv2.canonicalization.canonicalize import canonicalize, verifier

class QutipBackend(BackendBase):
    """
    Class representing the Qutip backend
    insprired from https://github.com/QuEraComputing/bloqade-python/blob/main/src/bloqade/ir/routine/braket.py#L183
    """

    def compile(self, task: Task):
        """
        Method for compiling a task to a [`QutipExperiment`][quantumion.backend.qutip.interface.QutipExperiment]

        Args:
            task (Task): Quantum experiment to compile
        """
        from quantumion.compilerv2.analog.assign import VerifyAnalogIRDim
        canonicalized_task = canonicalize(task)
        verifier(canonicalized_task)
        # add verifier which checks hilbert space dim

        canonicalized_circuit = canonicalized_task.program

        # pprint(canonicalized_circuit)
        
        assigned_circuit = Post(AssignAnalogIRDim())(canonicalized_circuit)

        canonicalized_args = canonicalized_task.args
        Post(VerifyAnalogIRDim(n_qreg=assigned_circuit.n_qreg, n_qmode=assigned_circuit.n_qmode))(assigned_circuit)
        Post(VerifyAnalogIRDim(n_qreg=assigned_circuit.n_qreg, n_qmode=assigned_circuit.n_qmode))(canonicalized_args)

        # here fock_cutoff is a compiler parameter

        converted_circuit = PostConversion(QutipBackendTransformer(fock_cutoff=task.args.fock_cutoff))(assigned_circuit)
        converted_args = PostConversion(QutipBackendTransformer(fock_cutoff=task.args.fock_cutoff))(canonicalized_args)
        # circuit_args = PostConversion(QutipBackendTransformer())(canonicalized_args)
        # pprint(converted_circuit)
        

        return QutipExperiment(
            instructions=converted_circuit,
            n_qreg=assigned_circuit.n_qreg,
            n_qmode = assigned_circuit.n_qmode,
            args = converted_args
        )

    def run(self, *, task: Task = None, experiment: QutipExperiment = None):
        """
        Method to run a

        Args:
            task (Optional[Task]): Quantum experiment to run as a [`Task`][quantumion.backend.task.Task] object
            experiment (Optional[QutipExperiment]): Quantum experiment to run as a [`QutipExperiment`][quantumion.backend.qutip.interface.QutipExperiment] object
        """
        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task=task)
        return PostConversion(QutipExperimentInterpreter())(experiment)


if __name__ == '__main__':
    from quantumion.compiler.analog.base import *
    from quantumion.interface.analog.operator import *
    from quantumion.interface.analog.operations import *
    from quantumion.backend.metric import *
    from rich import print as pprint
    from quantumion.backend.task import Task, TaskArgsAnalog
    X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

    ac = AnalogCircuit()
    ac.evolve(gate=AnalogGate(hamiltonian=1*(X@A)), duration=1)
    ac.evolve(gate=AnalogGate(hamiltonian=X@A + (X*I)@A), duration=1)
    # ac.n_qreg = 1
    # ac.n_qmode = 0
    args = TaskArgsAnalog(n_shots=100, metrics={
        'exp' : Expectation(operator=X@(A*LI)),
    })

    task = Task(
        program=ac,
        args = args
    )
    backend = QutipBackend()
    pprint(backend.run(task=task))