import tensorcircuit as tc

########################################################################################

from quantumion.backend.base import BackendBase
from quantumion.backend.task import Task, TaskResultDigital

from quantumion.interface.math import ComplexFloat
from quantumion.interface.digital.circuit import DigitalCircuit

########################################################################################


class TensorCircuitBackend(BackendBase):
    def __init__(self):
        self.kwargs = {}

    def run(self, task: Task) -> TaskResultDigital:
        assert isinstance(task.program, DigitalCircuit), "Wrong program type"
        circuit = task.program
        qasm = circuit.qasm
        print(qasm)
        circ = tc.Circuit.from_openqasm(qasm)

        print(circ.draw(output="text"))

        result = TaskResultDigital(
            counts=circ.sample(
                batch=task.args.repetitions, allow_state=True, format="count_dict_bin"
            ),
            state=list(map(ComplexFloat.from_np_complex128, circ.state())),
        )
        return result
