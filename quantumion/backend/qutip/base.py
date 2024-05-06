from quantumion.backend.qutip.visitor import (
    QutipBackendTransformer,
    QutipExperimentInterpreter,
)
from quantumion.backend.base import BackendBase
from quantumion.backend.qutip.interface import QutipExperiment
from quantumion.compiler.analog.analysis import (
    RegisterInformation,
)
from quantumion.backend.task import Task

from quantumion.compiler.flow import *
from quantumion.compiler.analog.verification_flow import VerificationFlow
########################################################################################
__all__ = [
    "QutipBackend",
]

class QutipBackendFlow(FlowGraph):
    nodes = [
        VerificationFlow(name = "verification_flow"),
        TransformerFlowNode(visitor=RegisterInformation(), name = 'register_information'),
        TransformerFlowNode(visitor=QutipBackendTransformer(), name = 'qutip_backend'),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "verification_flow"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_once(done="register_information")
    def forward_verification_flow(self, model):
        pass

    @forward_decorators.forward_once(done="qutip_backend")
    def forward_register_information(self, model):
        pass

    @forward_decorators.forward_once(done="terminal")
    def forward_qutip_backend(self, model):
        pass
    

class QutipBackend(BackendBase):

    @property
    def graph(self):
        return QutipBackendFlow(name="_")
    
    @property
    def evolve(self):
        return TransformerFlowNode(visitor=QutipExperimentInterpreter(),name="_")

    def compile(self, task: Task):
        return self.graph(task).model

    def run(self, *, task: Task = None, experiment: QutipExperiment = None):
        if task is not None and experiment is not None:
            raise TypeError("Both task and experiment are given as inputs to run")
        if experiment is None:
            experiment = self.compile(task=task)
        return self.evolve(experiment).model
    
