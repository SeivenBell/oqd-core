
def term_index_dim(lst):
    if isinstance(lst, int):
        return [1,0]
    if isinstance(lst, tuple):
        return [0,1]
    dim = [0,0]
    for elem in lst:
        if isinstance(elem, tuple):
            dim[1] = dim[1] + 1
        else:
            dim[0] = dim[0] + 1
    return dim