from quantumion.compiler.walk import Post
from quantumion.compiler.analog.rewrite.assign import AssignAnalogIRDim
from quantumion.compiler.analog.verify.task import VerifyAnalogArgsDim, VerifyAnalogCircuitDim
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
    assigned_model = Post(AssignAnalogIRDim())(model)
    Post(
        VerifyAnalogCircuitDim(
            n_qreg=assigned_model.n_qreg, n_qmode=assigned_model.n_qmode
        )
    )(assigned_model)
    return assigned_model


def verify_analog_args_dim(model, n_qreg, n_qmode):
    Post(VerifyAnalogArgsDim(n_qreg=n_qreg, n_qmode=n_qmode))(model)
