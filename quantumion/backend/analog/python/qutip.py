import itertools
import qutip as qt
import numpy as np
import time

########################################################################################

from quantumion.backend.base import BackendBase
from quantumion.backend.task import Task, DataAnalog, TaskArgsAnalog, TaskResultAnalog
from quantumion.backend.metric import *

from quantumion.interface.math import ComplexFloat
from quantumion.interface.analog.gate import AnalogGate
from quantumion.interface.analog.operator import Operator
from quantumion.interface.analog.circuit import AnalogCircuit
from quantumion.utils.math import prod

########################################################################################


class QutipBackend(BackendBase):
    name = "qutip"

    def __init__(self):
        super().__init__()
        self.qreg_map = {}
        self.qmode_map = {}
        self.fmetrics = []

    def run(self, task: Task) -> TaskResultAnalog:
        start = time.time()

        assert isinstance(
            task.program, AnalogCircuit
        ), "Qutip backend only simulates Experiment objects."

        circuit = task.program
        args = task.args
        data = DataAnalog(metrics={key: np.empty(0) for key in args.metrics.keys()})

        # initialize and step through analog gates
        self._init_maps(args)
        self._initialize(circuit, args, data)
        self.fmetrics = {
            key: self._map_metric(metric, circuit)
            for (key, metric) in args.metrics.items()
        }

        t0 = 0.0
        for statement in circuit.sequence:
            if statement.key == "initialize":
                continue  # todo: implement simulation logic of initializing/measuring qregs/qmodes

            elif statement.key == "evolve":
                self._evolve(statement.gate, args, data, t0)
                t0 += statement.gate.duration

            elif statement.key == "measure":
                continue  # todo

        self._measure(circuit, args, data)

        runtime = time.time() - start

        # get measurement data
        bitstrings = ["".join(map(str, shot)) for shot in data.shots]
        counts = {bitstring: bitstrings.count(bitstring) for bitstring in bitstrings}

        # create result object to return
        result = TaskResultAnalog(
            counts=counts,
            metrics=data.metrics,
            times=data.times.tolist(),
            # todo: improve mapping between custom ComplexFloat type and numpy
            state=list(
                map(ComplexFloat.from_np_complex128, data.state.full().squeeze())
            ),
            runtime=runtime,
        )
        return result

    def _init_maps(self, spec: TaskArgsAnalog):
        self.qreg_map = {
            "i": qt.qeye(2),
            "x": qt.sigmax(),
            "y": qt.sigmay(),
            "z": qt.sigmaz(),
        }
        self.qmode_map = {
            0: qt.qeye(spec.fock_cutoff),
            1: qt.create(spec.fock_cutoff),
            -1: qt.destroy(spec.fock_cutoff),
        }

    def _initialize(
        self, circuit: AnalogCircuit, args: TaskArgsAnalog, data: DataAnalog
    ):
        # generate initial quantum state as the |00.0> \otimes |00.0> as Qobj
        dims = circuit.n_qreg * [2] + circuit.n_qmode * [args.fock_cutoff]
        data.state = qt.tensor([qt.basis(d, 0) for d in dims])
        return

    def _evolve(
        self, gate: AnalogGate, args: TaskArgsAnalog, data: DataAnalog, t0: float
    ):
        options = qt.solver.Options(store_final_state=True)
        duration = gate.duration
        tspan = np.linspace(
            0, duration, round(duration / args.dt)
        )  # create time vector

        op_qobj = self._map_gate_to_qobj(gate)

        # run the Qutip solver
        # todo: switch to mesolve if using dissipative terms
        result_qobj = qt.sesolve(
            op_qobj, data.state, tspan, e_ops=self.fmetrics, options=options
        )

        data.times = np.hstack([data.times, t0 + tspan])
        data.metrics = {
            key: np.hstack([data.metrics[key], result_qobj.expect[key]])
            for key in data.metrics.keys()
        }
        data.state = result_qobj.final_state
        return

    def _measure(self, circuit: AnalogCircuit, args: TaskArgsAnalog, data: DataAnalog):
        if args.n_shots is not None:
            state = data.state
            probs = np.power(np.abs(state.full()), 2).squeeze()
            inds = np.random.choice(len(probs), size=args.n_shots, p=probs)
            opts = circuit.n_qreg * [[0, 1]] + circuit.n_qmode * [
                list(range(args.fock_cutoff))
            ]
            bases = list(itertools.product(*opts))
            shots = np.array([bases[ind] for ind in inds])
            data.shots = shots
        return

    def _map_operator_to_qobj(self, operator: Operator) -> qt.Qobj:
        """
        Maps an operator to the matching numerical Qutip QObj.

        Args:
            operator:

        Returns:

        """
        _operator_qobjs = []

        if operator.pauli:
            _operator_qobjs.append(
                qt.tensor([self.qreg_map[i] for i in operator.pauli])
            )

        if operator.ladder:
            _operator_qobjs.append(
                qt.tensor(
                    [prod([self.qmode_map[j] for j in tf]) for tf in operator.ladder]
                )
            )

        if isinstance(operator.coefficient, ComplexFloat):
            coefficient = operator.coefficient.real + 1j * operator.coefficient.imag
        elif isinstance(operator.coefficient, (int, float)):
            coefficient = operator.coefficient
        else:
            raise TypeError

        return coefficient * qt.tensor(_operator_qobjs)

    def _sum_operators(self, operators: List[Operator]):
        return sum([self._map_operator_to_qobj(operator) for operator in operators])

    def _map_gate_to_qobj(self, gate: AnalogGate) -> qt.Qobj:
        return self._sum_operators(gate.hamiltonian)

    def _map_metric(self, metric: Metric, circuit: AnalogCircuit):
        if isinstance(metric, EntanglementEntropyVN):
            f = lambda t, psi: entanglement_entropy_vn(
                t, psi, metric.qreg, metric.qmode, circuit.n_qreg, circuit.n_qmode
            )

        elif isinstance(metric, Expectation):
            f = lambda t, psi: qt.expect(self._sum_operators(metric.operator), psi)

        else:
            raise ValueError("Not a valid Metric for the Qutip backend.")

        return f


# todo: define all metrics to track during dynamics
def entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode):
    rho = qt.ptrace(
        psi,
        qreg
        + [n_qreg + m for m in qmode],  # canonical index for each local Hilbert space
    )
    return qt.entropy_vn(rho)
