from midstack.compiler.walk import Post
from midstack.compiler.analog.rule.assign import AssignAnalogIRDim
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

    Args:
        model (AnalogCircuit): n_qreg and n_qmode fields of [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] are not assigned

    Returns:
        model (AnalogCircuit): n_qreg and n_qmode fields of [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] are assigned

    Assumptions:
        All [`Operator`][midstack.interface.analog.operator.Operator] inside [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] must be canonicalized
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

    Args:
        model (TaskArgsAnalog):

    Returns:
        model (TaskArgsAnalog):

    Assumptions:
        All  [`Operator`][midstack.interface.analog.operator.Operator] inside TaskArgsAnalog must be canonicalized
    """
    Post(VerifyAnalogArgsDim(n_qreg=n_qreg, n_qmode=n_qmode))(model)
