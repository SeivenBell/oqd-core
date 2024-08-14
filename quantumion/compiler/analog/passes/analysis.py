from quantumion.compiler.analog.analysis import TermIndex
from quantumion.compiler.walk import In

def analysis_term_index(model):
    analysis = In(TermIndex())
    analysis(model=model)
    return analysis.children[0].term_idx