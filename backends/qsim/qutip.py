import itertools
import qutip as qt
import numpy as np

from quantumion.backend.base import Backend, Result, Specification
from quantumion.hamiltonian.base import Operator
from quantumion.hamiltonian.experiment import Experiment, Evolve, Measure, Initialize
from quantumion.hamiltonian.utils import prod


class QutipBackend(Backend):
    """
        Wraps qutip functionality, which will be called by the Qutipbackend.
    """

    def __init__(self, qmode_trunc=4):
        super().__init__()

        self.qmode_trunc = qmode_trunc  # truncation for Fock basis
        self.qreg_map = {
            0: qt.qeye(2),
            1: qt.sigmax(),
            2: qt.sigmay(),
            3: qt.sigmaz()
        }
        self.qmode_map = {
            0: qt.qeye(qmode_trunc),
            1: qt.create(qmode_trunc),
            -1: qt.destroy(qmode_trunc),
        }

    def run_experiment(self, experiment: Experiment, spec: Specification) -> Result:
        # Hilbert space dimensions of the composite, n-ion, m-phonon space
        """
        :param experiment: Experiment: Pass the test_hamiltonian object to the function
        :param spec: Specification: Specify the time and number of steps
        :return: A result object
        """

        experiment.check()

        result = Result()
        for statement in experiment.seq:
            if isinstance(statement, Initialize):
                result = self._initialize(experiment.dim_qreg, experiment.dim_qmode, spec, result)

            elif isinstance(statement, Evolve):
                op = experiment.ops[statement.name]
                result = self._evolve(op, statement.time, spec, result)

            elif isinstance(statement, Measure):
                result = self._measure(experiment.dim_qreg, experiment.dim_qmode, spec, result)

            else:
                raise RuntimeError

        return result

    def _initialize(self, dim_p, dim_f, spec: Specification, result: Result):
        # generate initial quantum state as the |00.0> \otimes |00.0> as Qobj
        dims = dim_p * [2] + dim_f * [self.qmode_trunc]
        result.state = qt.tensor([qt.basis(d, 0) for d in dims])
        return result

    def _evolve(self, op, time, spec: Specification, result: Result):
        options = qt.solver.Options(store_final_state=True)
        times = np.linspace(0, time, round(time/spec.dt))  # create time vector

        obs_qobjs = {key: self._map_operator_to_qobj(obs) for key, obs in spec.observables.items()}
        op_qobj = self._map_operator_to_qobj(op)

        # run the Qutip solver
        result_qobj = qt.mesolve(op_qobj, result.state, times, [], obs_qobjs, options=options)

        # result.observables = {name: result_qobj.expect[i] for i, name in enumerate(spec.observables.keys())}
        result = self._update_observables(spec, result, result_qobj)

        if result.times:
            result.times += list(times + result.times[-1])
        else:
            result.times += list(times)

        result.state = result_qobj.final_state
        return result

    def _measure(self, dim_p, dim_f, spec: Specification, result: Result):

        if spec.n_samples is not None:
            if spec.measurement_basis == "x":
                local_rot = qt.sigmax()
            elif spec.measurement_basis == "y":
                local_rot = qt.sigmay()
            elif spec.measurement_basis == "z":
                local_rot = qt.identity(2)
            else:
                raise ValueError("Not a valid measurement basis.")

            measurement_rot = qt.tensor(
                dim_p * [local_rot]
                + dim_f * [qt.identity(self.qmode_trunc)]
            )
            state = measurement_rot * result.state

            probs = np.power(np.abs(state.full()), 2).squeeze()
            inds = np.random.choice(len(probs), size=spec.n_samples, p=probs)
            opts = dim_p * [[1, -1]] + dim_f * [list(range(self.qmode_trunc))]
            bases = list(itertools.product(*opts))
            samples = np.array([bases[ind] for ind in inds])

            result.bases = bases
            result.samples = samples

        return result

    def _map_operator_to_qobj(self, operator: Operator) -> qt.Qobj:
        dims = operator.dim_qreg * [2] + operator.dim_qmode * [self.qmode_trunc]
        op_qobj = qt.Qobj(dims=2 * [dims])

        for c, t in operator.data:
            if not isinstance(c, (float, int, complex)):
                raise NotImplementedError("Coefficient type not supported yet for Qutip server.")

            _h = []
            if t["qreg"]:
                _h.append(qt.tensor([self.qreg_map[i] for i in t["qreg"]]))
            if t["qmode"]:
                _h.append(
                    qt.tensor([prod([self.qmode_map[j] for j in tf]) for tf in t["qmode"]])
                )
            op_qobj += c * qt.tensor(_h)
        return op_qobj

    def _update_observables(self, spec, result, result_qobj):
        for i, name in enumerate(spec.observables.keys()):
            if name not in result.observables.keys():
                result.observables[name] = list(result_qobj.expect[i])  # add to results
            else:
                result.observables[name] += list(result_qobj.expect[i])  # update results
            # result.observables = {name: result_qobj.expect[i] for i, name in enumerate(spec.observables.keys())}
        return result
