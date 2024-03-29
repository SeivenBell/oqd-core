import numpy as np

def amplitude(state: list):
    amplitudes = []
    for x in state:
        amplitudes.append(np.sqrt(x.real**2 + x.imag**2))
    return amplitudes