from quantumion.backend.qutip.visitor import (
    QutipBackendTransformer,
    QutipExperimentEvolve,
    QutipTaskArgsCanonicalization,
)
from quantumion.backend.base import BackendBase
from quantumion.backend.qutip.interface import QutipExperiment
from quantumion.compiler.analog.interface import (
    RegisterInformation,
    AnalogCircuitCanonicalization,
)
from quantumion.backend.task import Task

########################################################################################
__all__ = [
    "QutipBackend",
]


class QutipBackend(BackendBase):

    def compile(self, task: Task):
        circuit = task.program.accept(AnalogCircuitCanonicalization())
        args = task.args.accept(QutipTaskArgsCanonicalization())
        return circuit.accept(RegisterInformation()).accept(
            QutipBackendTransformer(args=args)
        )

    def run(self, *, task: Task = None, experiment: QutipExperiment = None):
        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task=task)
        return experiment.accept(QutipExperimentEvolve())
