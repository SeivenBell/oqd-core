from midstack.interface.analog.operator import *
from midstack.interface.analog.operations import *
from midstack.backend.task import TaskArgsAnalog, TaskResultAnalog, ComplexFloat
from midstack.compiler.math.passes import evaluate_math_expr
from midstack.backend.qutip.interface import (
    QutipExperiment,
    QutipOperation,
    QutipMeasurement,
    TaskArgsQutip,
    QutipExpectation,
)
from midstack.backend.metric import *
from midstack.backend.task import Task, TaskArgsAnalog
import qutip as qt
from midstack.compiler.walk import *
from midstack.compiler.rule import *
import numpy as np
import itertools
import time


def entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode):
    rho = qt.ptrace(
        psi,
        qreg + [n_qreg + m for m in qmode],
    )
    return qt.entropy_vn(rho)


class QutipMetricConversion(ConversionRule):
    """
    This takes in a a dictionary containing Metrics, which get converted to lambda functions for QuTip

    Args:
        model (dict): The values are Analog layer Operators

    Returns:
        model (dict): The values are lambda functions

    Note:
        n_qreg and n_qmode are given as compiler parameters
    """

    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._n_qreg = n_qreg
        self._n_qmode = n_qmode

    def map_QutipExpectation(self, model: QutipExpectation, operands):
        for idx, operator in enumerate(model.operator):
            coefficient = evaluate_math_expr(operator[1])
            op_exp = (
                coefficient * operator[0]
                if idx == 0
                else op_exp + coefficient * operator[0]
            )
        return lambda t, psi: qt.expect(op_exp, psi)

    def map_EntanglementEntropyVN(self, model: EntanglementEntropyVN, operands):
        return lambda t, psi: entanglement_entropy_vn(
            t, psi, model.qreg, model.qmode, self._n_qreg, self._n_qmode
        )


class QutipExperimentVM(RewriteRule):
    """
    This is a Virtual Machine which takes in a QutipExperiment object, simulates the experiment and then produces the results

    Args:
        model (QutipExperiment): This is the compiled  [`QutipExperiment`][midstack.backend.qutip.interface.QutipExperiment] object

    Returns:
        task (TaskResultAnalog):

    Note:
        n_qreg and n_qmode are given as compiler parameters
    """

    def __init__(self, qt_metrics, n_shots, fock_cutoff, dt):
        super().__init__()
        self.results = TaskResultAnalog(runtime=0)
        self._qt_metrics = qt_metrics
        self._n_shots = n_shots
        self._fock_cutoff = fock_cutoff
        self._dt = dt

    def map_QutipExperiment(self, model: QutipExperiment):

        dims = model.n_qreg * [2] + model.n_qmode * [self._fock_cutoff]
        self.n_qreg = model.n_qreg
        self.n_qmode = model.n_qmode
        self.current_state = qt.tensor([qt.basis(d, 0) for d in dims])

        self.results.times.append(0.0)
        self.results.state = list(
            self.current_state.full().squeeze(),
        )
        self.results.metrics.update(
            {
                key: [self._qt_metrics[key](0.0, self.current_state)]
                for key in self._qt_metrics.keys()
            }
        )

    def map_QutipMeasurement(self, model: QutipMeasurement):
        if self._n_shots is None:
            self.results.counts = {}
        else:
            print(self.current_state)
            probs = np.power(np.abs(self.current_state.full()), 2).squeeze()
            n_shots = self._n_shots
            inds = np.random.choice(len(probs), size=n_shots, p=probs)
            opts = self.n_qreg * [[0, 1]] + self.n_qmode * [
                list(range(self._fock_cutoff))
            ]
            bases = list(itertools.product(*opts))
            shots = np.array([bases[ind] for ind in inds])
            bitstrings = ["".join(map(str, shot)) for shot in shots]
            self.results.counts = {
                bitstring: bitstrings.count(bitstring) for bitstring in bitstrings
            }

        self.results.state = list(
            self.current_state.full().squeeze(),
        )

    def map_QutipOperation(self, model: QutipOperation):

        duration = model.duration
        tspan = np.linspace(0, duration, round(duration / self._dt)).tolist()

        qutip_hamiltonian = []
        for op, coeff in model.hamiltonian:
            qutip_hamiltonian.append([op, evaluate_math_expr(coeff, output_mode="str")])

        start_runtime = time.time()
        result_qobj = qt.sesolve(
            qutip_hamiltonian,
            self.current_state,
            tspan,
            e_ops=self._qt_metrics,
            options={"store_states": True},
        )
        self.results.runtime = time.time() - start_runtime + self.results.runtime

        self.results.times.extend([t + self.results.times[-1] for t in tspan][1:])

        for idx, key in enumerate(self.results.metrics.keys()):
            self.results.metrics[key].extend(result_qobj.expect[idx].tolist()[1:])

        self.current_state = result_qobj.final_state

        self.results.state = list(
            result_qobj.final_state.full().squeeze(),
        )


class QutipBackendCompiler(ConversionRule):
    """
    This is a ConversionRule which which compiles analog layer objects to QutipExperiment objects

    Args:
        model (VisitableBaseModel): This takes in objects in Analog level and converts them to representations which can be used to run QuTip simulations.

    Returns:
        model (Union[VisitableBaseModel, Any]): QuTip objects and representations which can be used to run QuTip simulations

    """

    def __init__(self, fock_cutoff=None):
        super().__init__()
        self._fock_cutoff = fock_cutoff

    def map_AnalogCircuit(self, model: AnalogCircuit, operands):
        return QutipExperiment(
            instructions=operands["sequence"],
            n_qreg=operands["n_qreg"],
            n_qmode=operands["n_qmode"],
        )

    def map_TaskArgsAnalog(self, model: TaskArgsAnalog, operands):
        return TaskArgsQutip(
            layer=model.layer,
            n_shots=model.n_shots,
            fock_cutoff=model.fock_cutoff,
            dt=model.dt,
            metrics=operands["metrics"],
        )

    def map_Expectation(self, model: Expectation, operands):
        return QutipExpectation(operator=operands["operator"])

    def map_Evolve(self, model: Evolve, operands):
        return QutipOperation(
            hamiltonian=operands["gate"],
            duration=model.duration,
        )

    def map_Measure(self, model: Measure, operands):
        return QutipMeasurement()

    def map_AnalogGate(self, model: AnalogGate, operands):
        return operands["hamiltonian"]

    def map_OperatorAdd(self, model: OperatorAdd, operands):
        op = operands["op1"]
        op.append(operands["op2"][0])
        return op

    def map_OperatorScalarMul(self, model: OperatorScalarMul, operands):
        return [(operands["op"], model.expr)]

    def map_PauliI(self, model: PauliI, operands) -> qt.Qobj:
        return qt.qeye(2)

    def map_PauliX(self, model: PauliX, operands) -> qt.Qobj:
        return qt.sigmax()

    def map_PauliY(self, model: PauliY, operands) -> qt.Qobj:
        return qt.sigmay()

    def map_PauliZ(self, model: PauliZ, operands) -> qt.Qobj:
        return qt.sigmaz()

    def map_Identity(self, model: Identity, operands) -> qt.Qobj:
        return qt.qeye(self._fock_cutoff)

    def map_Creation(self, model: Creation, operands) -> qt.Qobj:
        return qt.create(self._fock_cutoff)

    def map_Annihilation(self, model: Annihilation, operands) -> qt.Qobj:
        return qt.destroy(self._fock_cutoff)

    def map_OperatorMul(self, model: OperatorMul, operands) -> qt.Qobj:
        return operands["op1"] * operands["op2"]

    def map_OperatorKron(self, model: OperatorKron, operands) -> qt.Qobj:
        return qt.tensor(operands["op1"], operands["op2"])
