from midstack.compiler.walk import Post
from midstack.compiler.analog.rewrite.assign import AssignAnalogIRDim
from midstack.compiler.analog.verify.task import (
    VerifyAnalogArgsDim,
    VerifyAnalogCircuitDim,
)

########################################################################################

__all__ = [
    "assign_analog_circuit_dim",
    "verify_analog_args_dim",
]

########################################################################################


def assign_analog_circuit_dim(model):
    """
    This pass assigns n_qreg and n_qmode in the analog circuit and then verifies the assignment
    """
    assigned_model = Post(AssignAnalogIRDim())(model)
    Post(
        VerifyAnalogCircuitDim(
            n_qreg=assigned_model.n_qreg, n_qmode=assigned_model.n_qmode
        )
    )(assigned_model)
    return assigned_model


def verify_analog_args_dim(model, n_qreg, n_qmode):
    """
    This pass checks whether the assigned n_qreg and n_qmode in AnalogCircuit match the n_qreg and n_qmode
    in any Operators (like the Operator inside Expectation) in TaskArgsAnalog
    """
    Post(VerifyAnalogArgsDim(n_qreg=n_qreg, n_qmode=n_qmode))(model)
