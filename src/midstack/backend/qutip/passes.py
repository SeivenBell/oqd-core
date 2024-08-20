from midstack.backend.qutip.conversion import (
    QutipBackendCompiler,
    QutipExperimentInterpreter,
)
from midstack.compiler.walk import Post


def compiler_analog_circuit_to_qutipIR(model, fock_cutoff):
    """
    This compiles ([`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] to a list of  [`QutipOperation`][midstack.backend.qutip.interface.QutipOperation] objects

    Args:
        model (AnalogCircuit):
        fock_cutoff (int): fock_cutoff for Ladder Operators

    Returns:
        (list(QutipOperation)):

    """
    return Post(QutipBackendCompiler(fock_cutoff=fock_cutoff))(model=model)


def compiler_analog_args_to_qutipIR(model):
    """
    This compiles TaskArgsAnalog to a list of TaskArgsQutip


    Args:
        model (TaskArgsAnalog):

    Returns:
        (TaskArgsQutip):

    """
    return Post(QutipBackendCompiler(fock_cutoff=model.fock_cutoff))(model=model)


def run_qutip_experiment(model):
    """
    This takes in a [`QutipExperiment`][midstack.backend.qutip.interface.QutipExperiment] and produces a TaskResultAnalog object

    Args:
        model (QutipExperiment):

    Returns:
        (TaskResultAnalog): Contains results of the simulation

    """
    n_qreg = model.n_qreg
    n_qmode = model.n_qmode
    return Post(QutipExperimentInterpreter(n_qreg=n_qreg, n_qmode=n_qmode))(model=model)
