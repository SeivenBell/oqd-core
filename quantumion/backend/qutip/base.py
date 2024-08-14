from quantumion.backend.base import BackendBase
from quantumion.backend.qutip.interface import QutipExperiment

from quantumion.backend.task import Task

########################################################################################
__all__ = [
    "QutipBackend",
]


class QutipBackend(BackendBase):
    """
    Class representing the Qutip backend
    """

    def compile(self, task: Task):
        """
        Method for compiling a task to a [`QutipExperiment`][quantumion.backend.qutip.interface.QutipExperiment]

        Args:
            task (Task): Quantum experiment to compile
        """
        from quantumion.compiler.analog.passes.canonicalize import (
            analog_operator_canonicalization,
        )
        from quantumion.compiler.analog.passes.assign import (
            assign_analog_circuit_dim,
            verify_analog_args_dim,
        )
        from quantumion.backend.qutip.passes import (
            compiler_analog_args_to_qutipIR,
            compiler_analog_circuit_to_qutipIR,
        )

        canonicalized_circuit = analog_operator_canonicalization(task.program)
        canonicalized_args = analog_operator_canonicalization(task.args)

        assigned_circuit = assign_analog_circuit_dim(canonicalized_circuit)
        verify_analog_args_dim(
            canonicalized_args,
            n_qreg=assigned_circuit.n_qreg,
            n_qmode=assigned_circuit.n_qmode,
        )
        # here fock_cutoff is a compiler parameter
        converted_circuit = compiler_analog_circuit_to_qutipIR(
            assigned_circuit, fock_cutoff=task.args.fock_cutoff
        )
        converted_args = compiler_analog_args_to_qutipIR(
            canonicalized_args, fock_cutoff=task.args.fock_cutoff
        )

        return QutipExperiment(
            instructions=converted_circuit,
            n_qreg=assigned_circuit.n_qreg,
            n_qmode=assigned_circuit.n_qmode,
            args=converted_args,
        )

    def run(self, *, task: Task = None, experiment: QutipExperiment = None):
        """
        Method to run a

        Args:
            task (Optional[Task]): Quantum experiment to run as a [`Task`][quantumion.backend.task.Task] object
            experiment (Optional[QutipExperiment]): Quantum experiment to run as a [`QutipExperiment`][quantumion.backend.qutip.interface.QutipExperiment] object
        """
        from quantumion.backend.qutip.passes import run_qutip_experiment

        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task=task)
        return run_qutip_experiment(experiment)
