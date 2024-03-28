from quantumion.backend.qutip.visitor import QutipBackendTransformer, QutipExperimentEvolve
from quantumion.backend.qutip.interface import QutipExperiment
from quantumion.compiler.analog.interface import RegisterInformation
from quantumion.backend.task import Task

########################################################################################

class QutipBackend():

    def compile(self, task: Task):
        circuit = task.program
        args = task.args
        return circuit.accept(RegisterInformation()).accept(QutipBackendTransformer(args=args))

    def run(self, task: Task = None, experiment: QutipExperiment = None):
        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task = task)
        return experiment.accept(QutipExperimentEvolve())
