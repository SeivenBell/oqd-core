from quantumion.backend.qutip.conversion import (
    QutipBackendCompiler,
    QutipExperimentInterpreter,
)
from quantumion.compiler.walk import Post


def compiler_analog_circuit_to_qutipIR(model, fock_cutoff):
    """
    This compiles AnalogCircuit to a list of QutipOperation objects
    """
    return Post(QutipBackendCompiler(fock_cutoff=fock_cutoff))(model=model)


def compiler_analog_args_to_qutipIR(model):
    """
    This compiles TaskArgsAnalog to a list of TaskArgsQutip
    """
    return Post(QutipBackendCompiler(fock_cutoff=model.fock_cutoff))(model=model)


def run_qutip_experiment(model):
    """
    This takes in an AnalogCircuit and produces a QutipExperiment object
    """
    n_qreg = model.n_qreg
    n_qmode = model.n_qmode
    return Post(QutipExperimentInterpreter(n_qreg=n_qreg,
                                           n_qmode=n_qmode))(model=model)
