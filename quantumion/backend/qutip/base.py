from typing import Optional

########################################################################################

from quantumion.backend.qutip.visitor import (
    QutipBackendTransformer,
    QutipExperimentEvolve,
    QutipTaskArgsCanonicalization,
    AnalogCircuitCanonicalization,
)
from quantumion.backend.base import BackendBase
from quantumion.backend.qutip.interface import QutipExperiment
from quantumion.compiler.analog.analysis import (
    RegisterInformation,
)
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
        circuit = task.program.accept(AnalogCircuitCanonicalization())
        args = task.args.accept(QutipTaskArgsCanonicalization())
        return circuit.accept(RegisterInformation()).accept(
            QutipBackendTransformer(args=args)
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
        return experiment.accept(QutipExperimentEvolve())
