from oqd_compiler_infrastructure import In

########################################################################################


from ..analysis import TermIndex

########################################################################################


def analysis_term_index(model):
    """
    This pass computes and returns the TermIndex of an operator
    and returns a 2d list.

    Args:
        model: Operator

    Returns:
        dim (list[list[Union[int, tuple]]]):

    Example:
        for model = X@Y, the output is [[1,2]]
        for model = X + Y the output is [[1], [2]]
    """
    analysis = In(TermIndex())
    analysis(model=model)
    return analysis.children[0].term_idx


def analysis_canonical_hamiltonian_dim(model):
    """
    This pass computes the dimension of a canonicalized [`Operator`][midstack.interface.analog.operator.Operator] and returns the dimension
    as a tuple (n_qreg, n_qmode), where n_qreg is for number of quantum registers
    and n_qmode is for number of quantum modes.

    Args:
        model (Operator): [`Operator`][midstack.interface.analog.operator.Operator] of Analog level

    Returns:
        tupe(int,int)

    Example:
        for model = X@Y, the output is (2,0) where 2 is for number of quantum registers
        and 0 is for number of quantum modes
    """
    analysis = In(TermIndex())
    analysis(model=model)
    term = analysis.children[0].term_idx[0]

    dim = (0, 0)
    for elem in term:
        if isinstance(elem, tuple):
            dim = (dim[0], dim[1] + 1)
        else:
            dim = (dim[0] + 1, dim[1])
    return dim
