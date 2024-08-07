from quantumion.compilerv2.walk import Post
from quantumion.compilerv2.analog.rewrite.assign import (
    AssignAnalogIRDim,
    VerifyAnalogCircuitDim,
    VerifyAnalogArgsDim,
)

########################################################################################

__all__ = [
    "assign_analog_circuit_dim",
    "verify_analog_args_dim",
]

########################################################################################


def assign_analog_circuit_dim(model):
    """can't have a chain here as verifier need info which is obtained from assignanalogIRDim.
    Here we should probably use some sort of analysis pass to first get n_qreg and n_qmode, which can
    then be assigned by AssignAnalogIRDim"""
    assignmed_model = Post(AssignAnalogIRDim())(model)
    Post(
        VerifyAnalogCircuitDim(
            n_qreg=assignmed_model.n_qreg, n_qmode=assignmed_model.n_qmode
        )
    )(assignmed_model)
    return assignmed_model


def verify_analog_args_dim(model, n_qreg, n_qmode):
    Post(VerifyAnalogArgsDim(n_qreg=n_qreg, n_qmode=n_qmode))(model)
