import itertools
import qutip as qt
import numpy as np
from dataclasses import dataclass, field

from backends.base import Specification, Result, Submission

from quantumion.hamiltonian.operator import Operator
from quantumion.hamiltonian.coefficients import Complex
from quantumion.hamiltonian.experiment import Experiment
from quantumion.hamiltonian.utils import prod


@dataclass
class Data:
    times: np.array = None
    state: np.array = None
    observables: np.array = None
    shots: np.array = None


class QutipBackend:

    def __init__(self):
        super().__init__()
        self.qreg_map = {}
        self.qmode_map = {}

    def run(self, submission: Submission) -> Result:
        assert isinstance(submission.program, Experiment), "Qutip backend only simulates Experiment objects."
        experiment = submission.program
        spec = submission.specification
        data = Data()

        self._init_maps(spec)

        self._initialize(experiment, spec, data)
        for operator in experiment.sequence:
            time = 1.0  # todo: add to Experiment class
            self._evolve(operator, time, spec, data)

        self._measure(experiment, spec, data)

        result = Result()
        bitstrings = [''.join(map(str, shot)) for shot in data.shots]
        print(bitstrings)
        counts = {bitstring: bitstrings.count(bitstring) for bitstring in bitstrings}
        result.counts = counts

        return result

    """
    
    """
    def _init_maps(self, spec: Specification):
        self.qreg_map = {
            0: qt.qeye(2),
            1: qt.sigmax(),
            2: qt.sigmay(),
            3: qt.sigmaz()
        }
        self.qmode_map = {
            0: qt.qeye(spec.fock_trunc),
            1: qt.create(spec.fock_trunc),
            -1: qt.destroy(spec.fock_trunc),
        }

    """
    
    """
    def _initialize(self, experiment: Experiment, spec: Specification, data: Data):
        # generate initial quantum state as the |00.0> \otimes |00.0> as Qobj
        dims = experiment.n_qreg * [2] + experiment.n_qmode * [spec.fock_trunc]
        data.state = qt.tensor([qt.basis(d, 0) for d in dims])
        return

    def _evolve(self, operator, time, spec: Specification, data: Data):
        options = qt.solver.Options(store_final_state=True)
        times = np.linspace(0, time, round(time/spec.dt))  # create time vector

        # obs_qobjs = {key: self._map_operator_to_qobj(obs) for key, obs in spec.observables.items()}
        obs_qobjs = {}  # observables to record during evolution
        op_qobj = self._map_operator_to_qobj(operator, spec)

        # run the Qutip solver
        result_qobj = qt.mesolve(op_qobj, data.state, times, [], obs_qobjs, options=options)

        data.observables = {name: result_qobj.expect[i] for i, name in enumerate(spec.observables.keys())}
        # result = self._update_observables(spec, data, result_qobj)

        if data.times is not None:
            data.times += list(times + data.times[-1])
        else:
            data.times = np.array(times)

        data.state = result_qobj.final_state
        return

    def _measure(self, experiment: Experiment, spec: Specification, data: Data):
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

    def _map_operator_to_qobj(self, operator: Operator, spec: Specification) -> qt.Qobj:
        dims = operator.n_qreg * [2] + operator.n_qmode * [spec.fock_trunc]
        op_qobj = qt.Qobj(dims=2 * [dims])

        for term in operator.terms:
            # if not isinstance(c, (float, int, complex)):
            #     raise NotImplementedError("Coefficient type not supported yet for Qutip server.")

            _term_qobjs = []
            if term.qreg:
                _term_qobjs.append(qt.tensor([self.qreg_map[i] for i in term.qreg]))
            if term.qmode:
                _term_qobjs.append(
                    qt.tensor([prod([self.qmode_map[j] for j in tf]) for tf in term.qmode])
                )
            if isinstance(term.coefficient, Complex):
                coefficient = term.coefficient.real + 1j * term.coefficient.imag
            elif isinstance(term.coefficient, (int, float)):
                coefficient = term.coefficient
            else:
                raise TypeError

            op_qobj += coefficient * qt.tensor(_term_qobjs)
        return op_qobj

    # def _update_observables(self, spec, result, result_qobj):
    #     for i, name in enumerate(spec.observables.keys()):
    #         if name not in result.observables.keys():
    #             result.observables[name] = list(result_qobj.expect[i])  # add to results
    #         else:
    #             result.observables[name] += list(result_qobj.expect[i])  # update results
    #         # result.observables = {name: result_qobj.expect[i] for i, name in enumerate(spec.observables.keys())}
    #     return result
