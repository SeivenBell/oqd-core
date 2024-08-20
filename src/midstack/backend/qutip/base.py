from midstack.backend.base import BackendBase
from midstack.backend.qutip.interface import QutipExperiment

from midstack.backend.task import Task

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
        Method for compiling a task to a [`QutipExperiment`][midstack.backend.qutip.interface.QutipExperiment]

        Args:
            task (Task): Quantum experiment to compile

        Returns:
            QutipExperiment containing the compiled experiment for Qutip
        """
        from midstack.compiler.analog.passes.canonicalize import (
            analog_operator_canonicalization,
        )
        from midstack.compiler.analog.passes.assign import (
            assign_analog_circuit_dim,
            verify_analog_args_dim,
        )
        from midstack.backend.qutip.passes import (
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
        converted_args = compiler_analog_args_to_qutipIR(canonicalized_args)

        return QutipExperiment(
            instructions=converted_circuit,
            n_qreg=assigned_circuit.n_qreg,
            n_qmode=assigned_circuit.n_qmode,
            args=converted_args,
        )

    def run(self, *, task: Task = None, experiment: QutipExperiment = None):
        """
        Method to simulate an experiment using theQuTip backend

        Args:
            task (Optional[Task]): Run experiment from a [`Task`][midstack.backend.task.Task] object
            experiment (Optional[QutipExperiment]): Run experiment from a [`QutipExperiment`][midstack.backend.qutip.interface.QutipExperiment] object

        Returns:
            TaskResultAnalog object containing the simulation results.

        Note:
            only one of task or experiment must provided
        """
        from midstack.backend.qutip.passes import run_qutip_experiment

        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task=task)
        return run_qutip_experiment(experiment)
