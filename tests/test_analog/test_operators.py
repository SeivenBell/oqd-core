from quantumion.datastruct.analog import *


print(PauliX * PauliY)
print(PauliX == PauliX)


def test_pauli_math():
    assert PauliX == PauliX
    assert PauliX * PauliZ == PauliY
    assert PauliX * PauliX == PauliI
    assert PauliZ * PauliZ == PauliI


test_pauli_math()
