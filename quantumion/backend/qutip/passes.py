from quantumion.backend.qutip.conversion import (
    QutipBackendCompiler,
    QutipExperimentInterpreter,
)
from quantumion.compiler.walk import Walk, Post
from quantumion.compiler.rule import ConversionRule
from quantumion.compiler.rewriter import Chain


def compiler_analog_circuit_to_qutipIR(model, fock_cutoff):
    return Post(QutipBackendCompiler(fock_cutoff=fock_cutoff))(model=model)


def compiler_analog_args_to_qutipIR(model, fock_cutoff):
    return Post(QutipBackendCompiler(fock_cutoff=fock_cutoff))(model=model)


def run_qutip_experiment(model):
    n_qreg = model.n_qreg
    n_qmode = model.n_qmode
    return Post(QutipExperimentInterpreter(n_qreg=n_qreg,
                                           n_qmode=n_qmode))(model=model)
