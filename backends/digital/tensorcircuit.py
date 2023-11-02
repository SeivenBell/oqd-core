import tensorcircuit as tc


class TensorCircuit:

    def __init__(self):

        self.kwargs = {}

    def run(self, task):
        assert isinstance(task.program, Experiment), "Qutip backend only simulates Experiment objects."
