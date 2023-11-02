import itertools
import qutip as qt
import numpy as np

from backends.analog.data import DataAnalog, TaskArgsAnalog, TaskResultAnalog
from backends.task import Task

from quantumion.analog.gate import AnalogGate
from quantumion.analog.operator import Operator
from quantumion.analog.coefficient import Complex
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.math import prod


class QutipBackend:

    def __init__(self):
        super().__init__()
        self.qreg_map = {}
        self.qmode_map = {}

    def run(self, task: Task) -> TaskResultAnalog:
        assert isinstance(task.program, AnalogCircuit), "Qutip backend only simulates Experiment objects."
        experiment = task.program
        args = task.args
        data = DataAnalog()

        self._init_maps(args)

        self._initialize(experiment, args, data)
        for gate in experiment.sequence:
            self._evolve(gate, args, data)
        self._measure(experiment, args, data)

        bitstrings = [''.join(map(str, shot)) for shot in data.shots]
        counts = {bitstring: bitstrings.count(bitstring) for bitstring in bitstrings}

        result = TaskResultAnalog(
            counts=counts,
            expect=data.expect,
            times=data.times.tolist()
        )
        return result

    """
    
    """
    def _init_maps(self, spec: TaskArgsAnalog):
        self.qreg_map = {
            'i': qt.qeye(2),
            'x': qt.sigmax(),
            'y': qt.sigmay(),
            'z': qt.sigmaz()
        }
        self.qmode_map = {
            0: qt.qeye(spec.fock_trunc),
            1: qt.create(spec.fock_trunc),
            -1: qt.destroy(spec.fock_trunc),
        }

    """
    
    """
    def _initialize(self, experiment: AnalogCircuit, args: TaskArgsAnalog, data: DataAnalog):
        # generate initial quantum state as the |00.0> \otimes |00.0> as Qobj
        dims = experiment.n_qreg * [2] + experiment.n_qmode * [args.fock_trunc]
        data.state = qt.tensor([qt.basis(d, 0) for d in dims])
        return

    def _evolve(self, gate: AnalogGate, args: TaskArgsAnalog, data: DataAnalog):
        options = qt.solver.Options(store_final_state=True)
        duration = gate.duration
        durations = np.linspace(0, duration, round(duration / args.dt))  # create time vector

        obs_qobjs = {key: self._map_operator_to_qobj(obs) for key, obs in args.observables.items()}
        op_qobj = self._map_gate_to_qobj(gate, args)

        # run the Qutip solver
        result_qobj = qt.mesolve(op_qobj, data.state, durations, [], obs_qobjs, options=options)

        # data.expect = {name: result_qobj.expect[i] for i, name in enumerate(args.observables.keys())}
        if data.times is not None:
            data.times += list(durations + data.times[-1])
        else:
            data.times = np.array(durations)

        self._update_observables(data, result_qobj, args)

        data.state = result_qobj.final_state
        return

    def _measure(self, experiment: AnalogCircuit, spec: TaskArgsAnalog, data: DataAnalog):
        if spec.n_shots is not None:
            state = data.state
            probs = np.power(np.abs(state.full()), 2).squeeze()
            inds = np.random.choice(len(probs), size=spec.n_shots, p=probs)
            opts = experiment.n_qreg * [[0, 1]] + experiment.n_qmode * [list(range(spec.fock_trunc))]
            bases = list(itertools.product(*opts))
            shots = np.array([bases[ind] for ind in inds])
            data.bases = bases
            data.shots = shots
        return

    def _map_operator_to_qobj(self, operator: Operator) -> qt.Qobj:
        _operator_qobjs = []

        if operator.qreg:
            _operator_qobjs.append(qt.tensor([self.qreg_map[i] for i in operator.qreg]))
        if operator.qmode:
            _operator_qobjs.append(
                qt.tensor([prod([self.qmode_map[j] for j in tf]) for tf in operator.qmode])
            )

        if isinstance(operator.coefficient, Complex):
            coefficient = operator.coefficient.real + 1j * operator.coefficient.imag
        elif isinstance(operator.coefficient, (int, float)):
            coefficient = operator.coefficient
        else:
            raise TypeError

        return coefficient * qt.tensor(_operator_qobjs)

    def _map_gate_to_qobj(self, gate: AnalogGate, spec: TaskArgsAnalog) -> qt.Qobj:
        dims = gate.n_qreg * [2] + gate.n_qmode * [spec.fock_trunc]
        _gate_obj = qt.Qobj(dims=2 * [dims])

        for operator in gate.unitary:
            _operator_qobj = self._map_operator_to_qobj(operator)
            _gate_obj += _operator_qobj

        return _gate_obj

    def _update_observables(self, data: DataAnalog, result_qobj, args: TaskArgsAnalog):
        for i, name in enumerate(args.observables.keys()):
            if name not in data.expect.keys():
                data.expect[name] = list(result_qobj.expect[i])  # add to results
            else:
                data.expect[name] += list(result_qobj.expect[i])  # update results
        return
