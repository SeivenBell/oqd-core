from quantumion.compiler.analog.analysis import TermIndex
from quantumion.compiler.walk import In

def analysis_term_index(model):
    analysis = In(TermIndex())
    analysis(model=model)
    return analysis.children[0].term_idx

def analysis_canonical_hamiltonian_dim(model):
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