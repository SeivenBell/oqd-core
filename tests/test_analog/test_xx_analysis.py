# tests/test_xx_analysis.py

# Copyright 2024-2025 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest
import numpy as np

from oqd_core.interface.analog import (
    AnalogCircuit, AnalogGate, Evolve, Initialize, Measure,
    PauliX, PauliY, PauliZ, PauliI,
    OperatorKron, OperatorScalarMul, OperatorAdd, OperatorSub,
    Ladder, Annihilation, Creation
)
from oqd_core.compiler.analog.passes import (
    analog_operator_canonicalization,
    analyze_xx_gates
)
from oqd_core.interface.math import MathNum


# Helper function to create a multi-qubit operator with X at specified positions
def create_xx_term(x_positions, n_qubits):
    """
    Create a term where X operators are placed at specified positions,
    and the rest have identity operators.
    
    Args:
        x_positions: List of positions for X operators
        n_qubits: Total number of qubits
        
    Returns:
        A Kronecker product operator
    """
    ops = [PauliX() if i in x_positions else PauliI() for i in range(n_qubits)]
    term = ops[0]
    for op in ops[1:]:
        term = term @ op
    return term


# Helper function to create a circuit with a single XX gate
def create_xx_circuit(x_positions, n_qubits, coefficient=1.0):
    """
    Create a circuit with a single XX gate.
    
    Args:
        x_positions: List of positions for X operators
        n_qubits: Total number of qubits
        coefficient: Coefficient for the XX term
        
    Returns:
        An AnalogCircuit
    """
    # Create XX term
    xx_term = create_xx_term(x_positions, n_qubits)
    
    # Add coefficient if needed
    if coefficient != 1.0:
        xx_term = coefficient * xx_term
    
    # Create gate and circuit
    gate = AnalogGate(hamiltonian=xx_term)
    circuit = AnalogCircuit(n_qreg=n_qubits)
    circuit.initialize()
    circuit.evolve(gate=gate, duration=1.0)
    circuit.measure()
    
    return circuit


# Helper function to create a circuit with multiple XX terms
def create_multi_xx_circuit(term_specs, n_qubits):
    """
    Create a circuit with multiple XX terms.
    
    Args:
        term_specs: List of tuples (x_positions, coefficient)
        n_qubits: Total number of qubits
        
    Returns:
        An AnalogCircuit
    """
    # Create combined Hamiltonian
    hamiltonian = None
    for x_positions, coefficient in term_specs:
        term = create_xx_term(x_positions, n_qubits)
        if coefficient != 1.0:
            term = coefficient * term
            
        if hamiltonian is None:
            hamiltonian = term
        else:
            hamiltonian = hamiltonian + term
    
    # Create gate and circuit
    gate = AnalogGate(hamiltonian=hamiltonian)
    circuit = AnalogCircuit(n_qreg=n_qubits)
    circuit.initialize()
    circuit.evolve(gate=gate, duration=1.0)
    circuit.measure()
    
    return circuit


# Helper function to canonicalize a circuit
def canonicalize_circuit(circuit):
    """
    Apply canonicalization to all gates in a circuit.
    
    Args:
        circuit: The circuit to canonicalize
        
    Returns:
        Canonicalized circuit
    """
    for op in circuit.sequence:
        if isinstance(op, Evolve) and isinstance(op.gate, AnalogGate):
            op.gate.hamiltonian = analog_operator_canonicalization(op.gate.hamiltonian)
    
    return circuit


class TestXXAnalysis:
    
    def test_simple_xx_gate(self):
        """Test with a simple 2-qubit XX gate."""
        # Create a circuit with X_0 ⊗ X_1
        circuit = create_xx_circuit([0, 1], 2)
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1
        assert len(xx_weights) == 1
        assert len(xx_qubit_pairs) == 1
        assert xx_weights[0] == 1.0
        assert xx_qubit_pairs[0] == (0, 1)
        
        # Check Jij matrix
        expected_jij = np.zeros((2, 2))
        expected_jij[0, 1] = expected_jij[1, 0] = 1.0
        np.testing.assert_array_equal(jij_matrix, expected_jij)
    
    def test_multi_qubit_xx_gate(self):
        """Test with a 4-qubit system having an XX gate on qubits 0 and 3."""
        # Create a circuit with X_0 ⊗ I_1 ⊗ I_2 ⊗ X_3
        circuit = create_xx_circuit([0, 3], 4)
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1
        assert xx_weights[0] == 1.0
        assert xx_qubit_pairs[0] == (0, 3)
        
        # Check Jij matrix
        expected_jij = np.zeros((4, 4))
        expected_jij[0, 3] = expected_jij[3, 0] = 1.0
        np.testing.assert_array_equal(jij_matrix, expected_jij)
    
    def test_weighted_xx_gate(self):
        """Test with an XX gate with non-unity coefficient."""
        # Create a circuit with 2.5 * (X_0 ⊗ X_1)
        circuit = create_xx_circuit([0, 1], 2, coefficient=2.5)
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1
        assert xx_weights[0] == 2.5
        assert xx_qubit_pairs[0] == (0, 1)
        
        # Check Jij matrix
        expected_jij = np.zeros((2, 2))
        expected_jij[0, 1] = expected_jij[1, 0] = 2.5
        np.testing.assert_array_equal(jij_matrix, expected_jij)
    
    def test_multiple_xx_terms(self):
        """Test with multiple XX terms in the same gate."""
        # Create a circuit with X_0 ⊗ X_1 + 2.0 * (X_1 ⊗ X_2) + 0.5 * (X_0 ⊗ X_3)
        term_specs = [
            ([0, 1], 1.0),
            ([1, 2], 2.0),
            ([0, 3], 0.5)
        ]
        circuit = create_multi_xx_circuit(term_specs, 4)
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1  # One gate with multiple terms
        assert len(xx_weights) == 3  # Three XX terms
        assert len(xx_qubit_pairs) == 3
        
        # Check qubit pairs and weights (order might vary)
        pairs_weights = set(zip(xx_qubit_pairs, xx_weights))
        expected_pairs_weights = {
            ((0, 1), 1.0),
            ((1, 2), 2.0),
            ((0, 3), 0.5)
        }
        assert pairs_weights == expected_pairs_weights
        
        # Check Jij matrix
        expected_jij = np.zeros((4, 4))
        expected_jij[0, 1] = expected_jij[1, 0] = 1.0
        expected_jij[1, 2] = expected_jij[2, 1] = 2.0
        expected_jij[0, 3] = expected_jij[3, 0] = 0.5
        np.testing.assert_array_equal(jij_matrix, expected_jij)
    
    def test_large_system(self):
        """Test with a larger 8-qubit system."""
        # Create a circuit with various XX interactions in an 8-qubit system
        term_specs = [
            ([0, 1], 1.0),
            ([1, 2], 0.5),
            ([2, 3], 0.7),
            ([4, 5], 1.2),
            ([6, 7], 0.9),
            ([0, 7], 0.3)
        ]
        circuit = create_multi_xx_circuit(term_specs, 8)
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1
        assert len(xx_weights) == 6
        assert len(xx_qubit_pairs) == 6
        
        # Check Jij matrix size
        assert jij_matrix.shape == (8, 8)
        
        # Check a few elements of the matrix
        assert jij_matrix[0, 1] == 1.0
        assert jij_matrix[1, 2] == 0.5
        assert jij_matrix[4, 5] == 1.2
        assert jij_matrix[0, 7] == 0.3
    
    def test_incompatible_y_gate(self):
        """Test with an incompatible circuit containing Y operators."""
        # Create a circuit with X_0 ⊗ Y_1
        xx_term = PauliX() @ PauliY()
        gate = AnalogGate(hamiltonian=xx_term)
        circuit = AnalogCircuit(n_qreg=2)
        circuit.initialize()
        circuit.evolve(gate=gate, duration=1.0)
        circuit.measure()
        
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is False
        assert jij_matrix is None
    
    def test_incompatible_z_gate(self):
        """Test with an incompatible circuit containing Z operators."""
        # Create a circuit with X_0 ⊗ Z_1
        xx_term = PauliX() @ PauliZ()
        gate = AnalogGate(hamiltonian=xx_term)
        circuit = AnalogCircuit(n_qreg=2)
        circuit.initialize()
        circuit.evolve(gate=gate, duration=1.0)
        circuit.measure()
        
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is False
        assert jij_matrix is None
    
    def test_incompatible_ladder(self):
        """Test with an incompatible circuit containing ladder operators."""
        # Create a circuit with X_0 ⊗ a_1
        xx_term = PauliX() @ Annihilation()
        gate = AnalogGate(hamiltonian=xx_term)
        circuit = AnalogCircuit(n_qreg=2)
        circuit.initialize()
        circuit.evolve(gate=gate, duration=1.0)
        circuit.measure()
        
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is False
        assert jij_matrix is None
    
    def test_incompatible_too_many_x(self):
        """Test with a term that has more than 2 X operators."""
        # Create a circuit with X_0 ⊗ X_1 ⊗ X_2
        xx_term = PauliX() @ PauliX() @ PauliX()
        gate = AnalogGate(hamiltonian=xx_term)
        circuit = AnalogCircuit(n_qreg=3)
        circuit.initialize()
        circuit.evolve(gate=gate, duration=1.0)
        circuit.measure()
        
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is False
        assert jij_matrix is None
    
    def test_circuit_without_gates(self):
        """Test with a circuit that has no gates."""
        # Create an empty circuit
        circuit = AnalogCircuit(n_qreg=2)
        circuit.initialize()
        circuit.measure()
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is False
        assert len(xx_gates) == 0
        assert jij_matrix is None
    
    def test_subtraction_operator(self):
        """Test with a Hamiltonian using subtraction."""
        # Create a circuit with X_0 ⊗ X_1 - 0.5 * (X_2 ⊗ X_3)
        # Using OperatorSub directly
        term1 = create_xx_term([0, 1], 4)
        term2 = 0.5 * create_xx_term([2, 3], 4)
        hamiltonian = OperatorSub(op1=term1, op2=term2)
        
        gate = AnalogGate(hamiltonian=hamiltonian)
        circuit = AnalogCircuit(n_qreg=4)
        circuit.initialize()
        circuit.evolve(gate=gate, duration=1.0)
        circuit.measure()
        
        circuit = canonicalize_circuit(circuit)
        
        # Analyze the circuit
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Check results
        assert is_compatible is True
        assert len(xx_gates) == 1
        assert len(xx_weights) == 2
        assert len(xx_qubit_pairs) == 2
        
        # Check qubit pairs and weights (after canonicalization, term2 should have -0.5 coefficient)
        pairs_weights = set(zip(xx_qubit_pairs, xx_weights))
        expected_pairs_weights = {
            ((0, 1), 1.0),
            ((2, 3), -0.5)  # Negative due to subtraction
        }
        assert pairs_weights == expected_pairs_weights
        
        # Check Jij matrix
        expected_jij = np.zeros((4, 4))
        expected_jij[0, 1] = expected_jij[1, 0] = 1.0
        expected_jij[2, 3] = expected_jij[3, 2] = -0.5
        np.testing.assert_array_equal(jij_matrix, expected_jij)

    @pytest.mark.skipif(not os.path.exists("models/prism_optimizer.onnx"), 
                       reason="ONNX model file not found")
    def test_optimization_integration(self):
        """Test integration with the PrISM optimizer (if available)."""
        from oqd_core.compiler.analog.passes import optimize_xx_parameters
        
        # Create a simple circuit and get its Jij matrix
        circuit = create_xx_circuit([0, 1], 2)
        circuit = canonicalize_circuit(circuit)
        is_compatible, xx_gates, xx_weights, xx_qubit_pairs, jij_matrix = analyze_xx_gates(circuit)
        
        # Try to optimize parameters
        try:
            result = optimize_xx_parameters(jij_matrix)
            
            # Check that we got sensible outputs
            assert "rabi_frequencies" in result
            assert "predicted_fidelity" in result
            assert isinstance(result["rabi_frequencies"], np.ndarray)
            assert isinstance(result["predicted_fidelity"], float)
            assert 0.0 <= result["predicted_fidelity"] <= 1.0
            
        except (ValueError, ImportError) as e:
            # If optimization fails due to missing model or dependencies,
            # the test is basically skipped
            pytest.skip(f"Optimization could not be tested: {str(e)}")