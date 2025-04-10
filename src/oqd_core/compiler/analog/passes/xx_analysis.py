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

from typing import List, Tuple, Dict, Optional, Set, Union
import numpy as np
from oqd_compiler_infrastructure import RewriteRule, In, Post

from oqd_core.interface.analog import (
    AnalogCircuit, AnalogGate, Evolve,
    PauliX, PauliY, PauliZ, PauliI,
    OperatorKron, OperatorScalarMul, OperatorAdd, OperatorSub,
    Ladder, Annihilation, Creation
)
from oqd_core.interface.math import MathNum, MathVar, MathAdd, MathMul, MathExpr

__all__ = [
    "XXGateAnalyzer",
    "analyze_xx_gates",
    "optimize_xx_parameters",
]


class XXGateAnalyzer(RewriteRule):
    """
    An analyzer that identifies XX gates in multi-qubit quantum circuits.

    This analyzer examines canonicalized circuits to detect XX interactions (weight-2 Pauli X strings),
    extract coupling strengths, and determine compatibility with XX-only hardware.
    """

    def __init__(self, verbose=False):
        super().__init__()
        self.xx_gates = []           # Gates with XX interactions
        self.xx_weights = []         # Coefficients of XX interactions
        self.xx_qubit_pairs = []     # Qubit pairs for XX interactions (i,j)
        self.current_gate = None     # Current gate being processed
        self.current_coefficient = 1.0  # Current coefficient being processed
        self.is_compatible = True    # Whether circuit is compatible
        self.found_non_xx_gate = False  # Whether non-XX gates were found
        self.has_time_dependence = False  # Whether circuit has time-dependent terms
        self.has_ladder_operators = False  # Whether circuit has ladder operators
        self.n_qubits = 0            # Number of qubits in the system
        self.verbose = verbose
        self.processed_ops = set()   # Track processed operators by their id()
        
    def map_AnalogGate(self, model):
        """Track the current gate."""
        if self.verbose:
            print(f"Processing AnalogGate: {model}")
        self.current_gate = model

    def map_Evolve(self, model):
        """Process Evolve operations to track gates."""
        if self.verbose:
            print(f"Processing Evolve: {model}")
        # Set the current gate to the gate being processed
        self.current_gate = model.gate
        if self.verbose:
            print(f"  Setting current_gate to: {self.current_gate}")

    def map_Ladder(self, model):
        """Mark circuit as incompatible if it contains ladder operators."""
        if self.verbose:
            print(f"Found ladder operator - not compatible with XX-only")
        self.has_ladder_operators = True
        self.is_compatible = False

    def map_PauliY(self, model):
        """Mark circuit as incompatible if it contains PauliY."""
        if self.verbose:
            print(f"Found PauliY - not compatible with XX-only")
        self.found_non_xx_gate = True
        self.is_compatible = False

    def map_PauliZ(self, model):
        """Mark circuit as incompatible if it contains PauliZ."""
        if self.verbose:
            print(f"Found PauliZ - not compatible with XX-only")
        self.found_non_xx_gate = True
        self.is_compatible = False

    def map_OperatorAdd(self, model):
        """Process addition of operators by examining each term."""
        # OperatorAdd nodes are traversed automatically without special handling
        pass

    def map_OperatorSub(self, model):
        """Process subtraction by treating it as addition with a negative coefficient."""
        # OperatorSub is handled by the canonicalization, which converts it to OperatorAdd
        pass

    def map_OperatorKron(self, model):
        """
        Process Kronecker product operators to identify XX gates.
        
        This method extracts the positions of X operators in multi-qubit systems.
        """
        op_id = id(model)

        # Skip if we've already processed this exact operator
        if op_id in self.processed_ops:
            return
        
        # Mark as processed
        self.processed_ops.add(op_id)

        if self.verbose:
            print(f"Processing OperatorKron: {model}")

        # Extract X operator positions from the Kronecker product
        x_positions = self._extract_x_positions(model)
        
        if self.verbose:
            print(f"  Found X operators at positions: {x_positions}")
            
        # If we found exactly 2 X operators, this is a valid XX gate
        if len(x_positions) == 2:
            if self.verbose:
                print(f"  Valid XX gate found between qubits {x_positions[0]} and {x_positions[1]}")
                
            # Add this XX interaction to our tracking
            self._add_xx_interaction(x_positions, self.current_coefficient)
            
        # If we found any other number of X operators, it's not a valid XX gate
        elif len(x_positions) != 0:
            if self.verbose:
                print(f"  Invalid gate: found {len(x_positions)} X operators, need exactly 2")
            self.found_non_xx_gate = True
            self.is_compatible = False

    def map_OperatorScalarMul(self, model):
        """
        Process scalar multiplication operators to identify XX gates.
        
        This method extracts coefficients and processes the inner operator structure.
        """
        op_id = id(model)

        # Skip if we've already processed this exact operator
        if op_id in self.processed_ops:
            return
        
        # Mark as processed
        self.processed_ops.add(op_id)

        if self.verbose:
            print(f"Processing OperatorScalarMul")
            print(f"  Coefficient type: {model.expr.__class__.__name__}")
            print(f"  Operator type: {model.op.__class__.__name__}")

        # Check for time-dependent coefficients
        if self._is_time_dependent(model.expr):
            if self.verbose:
                print(f"  Found time-dependent coefficient - not compatible")
            self.has_time_dependence = True
            self.found_non_xx_gate = True
            return

        # Extract coefficient
        old_coefficient = self.current_coefficient
        coefficient = self._extract_coefficient(model.expr)
        
        # Store the current coefficient for use by other methods
        self.current_coefficient = coefficient
        if self.verbose:
            print(f"  Setting current_coefficient to: {self.current_coefficient}")

        # Continue traversing to process the inner operator
        # When the visitor reaches an OperatorKron, it will use this coefficient
        
        # Restore the previous coefficient after processing children
        self.current_coefficient = old_coefficient

    def _extract_x_positions(self, op, base_position=0):
        """
        Extract the positions of X operators in a multi-qubit tensor product.
        
        Args:
            op: The operator to analyze
            base_position: The starting position for this branch of the operator tree
            
        Returns:
            list: Positions where X operators appear
        """
        # Base cases
        if isinstance(op, PauliX):
            return [base_position]
        if isinstance(op, (PauliI, PauliY, PauliZ, Ladder)):
            return []
            
        # Recursive case for OperatorKron
        if isinstance(op, OperatorKron):
            # Find the size of the right subtree
            right_size = self._count_qubits(op.op2)
            
            # Recursively find X positions in left and right branches
            left_positions = self._extract_x_positions(op.op1, base_position)
            right_positions = self._extract_x_positions(op.op2, base_position + 1)
            
            # Combine the results
            return left_positions + right_positions
            
        # Default for other operator types
        return []
        
    def _count_qubits(self, op):
        """
        Count the number of qubits represented by an operator.
        
        Args:
            op: The operator to analyze
            
        Returns:
            int: Number of qubits
        """
        # Base cases
        if isinstance(op, (PauliX, PauliY, PauliZ, PauliI, Ladder)):
            return 1
            
        # Recursive case for OperatorKron
        if isinstance(op, OperatorKron):
            return self._count_qubits(op.op1) + self._count_qubits(op.op2)
            
        # Default for other operator types
        return 1
        
    def _add_xx_interaction(self, qubit_pair, coefficient):
        """
        Add an XX interaction to our tracking.
        
        Args:
            qubit_pair: Tuple or list of qubit indices (i,j)
            coefficient: Coefficient for this interaction
        """
        if self.verbose:
            print(f"  Adding XX interaction: qubits {qubit_pair}, coefficient {coefficient}")
            
        # Update total number of qubits if needed
        max_qubit = max(qubit_pair)
        self.n_qubits = max(self.n_qubits, max_qubit + 1)
            
        # Add to our tracking lists
        if self.current_gate and self.current_gate not in self.xx_gates:
            self.xx_gates.append(self.current_gate)
            self.xx_weights.append(coefficient)
            self.xx_qubit_pairs.append(tuple(sorted(qubit_pair)))  # Sort to ensure consistent order
        else:
            # If this gate is already in our list, update the weight
            for i, gate in enumerate(self.xx_gates):
                if gate == self.current_gate and tuple(sorted(qubit_pair)) == self.xx_qubit_pairs[i]:
                    if self.verbose:
                        print(f"  Updating weight for gate {i} from {self.xx_weights[i]} to {coefficient}")
                    self.xx_weights[i] = coefficient
                    break

    def _is_time_dependent(self, expr):
        """
        Recursively check if a math expression contains time dependence.
        
        Args:
            expr: The math expression to check
            
        Returns:
            bool: True if time-dependent, False otherwise
        """
        # Direct check for time variable
        if isinstance(expr, MathVar) and expr.name == 't':
            return True

        # Check binary operations
        if hasattr(expr, 'expr1') and hasattr(expr, 'expr2'):
            return self._is_time_dependent(expr.expr1) or self._is_time_dependent(expr.expr2)

        # Check unary operations
        if hasattr(expr, 'expr'):
            return self._is_time_dependent(expr.expr)

        # Default: not time-dependent
        return False

    def _extract_coefficient(self, expr):
        """
        Extract the numerical coefficient from a math expression.
        
        Args:
            expr: The math expression
            
        Returns:
            float: The extracted coefficient
        """
        if isinstance(expr, MathNum):
            return expr.value
        elif isinstance(expr, MathMul):
            # For multiplication, try to extract coefficients from both sides
            coef1 = self._extract_coefficient(expr.expr1)
            coef2 = self._extract_coefficient(expr.expr2)
            return coef1 * coef2
        elif isinstance(expr, MathAdd):
            # For addition, this is more complex and would require full evaluation
            # For simplicity, we return a default value
            return 1.0
            
        # For other expression types, return a default
        if self.verbose:
            print(f"  Could not extract coefficient from {expr.__class__.__name__}")
        return 1.0

    def build_jij_matrix(self):
        """
        Build a coupling matrix (Jij) from the detected XX interactions.
        
        Returns:
            numpy.ndarray or None: Coupling matrix or None if circuit is incompatible
        """
        if self.found_non_xx_gate or not self.xx_qubit_pairs:
            if self.verbose:
                print(f"Cannot create Jij matrix: is_compatible={self.is_compatible}, xx_pairs={self.xx_qubit_pairs}")
            return None

        # Ensure n_qubits is at least the size needed for our pairs
        if self.n_qubits == 0 and self.xx_qubit_pairs:
            max_qubit = max(max(pair) for pair in self.xx_qubit_pairs)
            self.n_qubits = max_qubit + 1

        if self.verbose:
            print(f"Creating Jij matrix of size {self.n_qubits}x{self.n_qubits}")
            print(f"Coupling terms: {list(zip(self.xx_qubit_pairs, self.xx_weights))}")

        # Create the coupling matrix
        jij = np.zeros((self.n_qubits, self.n_qubits))
        
        # Fill in the coupling strengths
        for pair, weight in zip(self.xx_qubit_pairs, self.xx_weights):
            i, j = pair
            jij[i, j] += weight  # Add rather than assign to handle multiple terms
            jij[j, i] += weight  # Mirror for symmetry (XX interactions are symmetric)

        return jij


def analyze_xx_gates(circuit, verbose=False):
    """
    Analyze a quantum circuit to detect XX gate patterns and build a coupling matrix.
    
    Args:
        circuit: The quantum circuit to analyze
        verbose: Whether to print debugging information
        
    Returns:
        Tuple containing:
        - bool: Whether the circuit is compatible with XX-only analysis
        - List[AnalogGate]: List of gates with XX interactions
        - List[float]: List of coupling strengths
        - List[Tuple[int, int]]: List of qubit pairs for XX interactions
        - numpy.ndarray or None: Coupling matrix (Jij) or None if incompatible
    """
    if verbose:
        print(f"Analyzing circuit: {circuit}")
        if hasattr(circuit, 'n_qreg'):
            print(f"Circuit n_qreg: {circuit.n_qreg}, n_qmode: {circuit.n_qmode}")

    # Run the analyzer
    analyzer = XXGateAnalyzer(verbose=verbose)
    In(analyzer)(model=circuit)

    # Count total gates for reporting
    total_gates = 0
    if hasattr(circuit, 'sequence'):
        total_gates = sum(1 for op in circuit.sequence if isinstance(op, Evolve))
        
    if verbose:
        print(f"Analysis details:")
        print(f"  Total gates in circuit: {total_gates}")
        print(f"  XX gates found: {len(analyzer.xx_gates)}")
        print(f"  XX interactions found: {len(analyzer.xx_qubit_pairs)}")
        print(f"  Non-XX components found: {analyzer.found_non_xx_gate}")

    # Determine compatibility
    is_compatible = len(analyzer.xx_qubit_pairs) > 0 and not analyzer.found_non_xx_gate
    analyzer.is_compatible = is_compatible

    # Determine circuit size for matrix
    circuit_size = 0
    if hasattr(circuit, 'n_qreg') and circuit.n_qreg is not None:
        circuit_size = circuit.n_qreg
    else:
        # If circuit_size is not specified, use the maximum qubit index from detected interactions
        circuit_size = analyzer.n_qubits if analyzer.n_qubits > 0 else 2

    # Build the coupling matrix
    jij_matrix = analyzer.build_jij_matrix() if is_compatible else None

    if verbose:
        print(f"Analysis results:")
        print(f"  Compatible: {is_compatible}")
        print(f"  XX gates found: {len(analyzer.xx_gates)}")
        print(f"  XX interactions: {analyzer.xx_qubit_pairs}")
        print(f"  XX weights: {analyzer.xx_weights}")
        print(f"  Found non-XX gates: {analyzer.found_non_xx_gate}")
        print(f"  Has time dependence: {analyzer.has_time_dependence}")
        print(f"  Has ladder operators: {analyzer.has_ladder_operators}")
        if jij_matrix is not None:
            print(f"  Jij matrix shape: {jij_matrix.shape}")
            print(f"  Jij matrix:\n{jij_matrix}")

    return (
        is_compatible, 
        analyzer.xx_gates, 
        analyzer.xx_weights, 
        analyzer.xx_qubit_pairs,
        jij_matrix
    )


def optimize_xx_parameters(jij_matrix, onnx_model_path=None):
    """
    Optimize control parameters for an XX Hamiltonian using the PrISM model.
    
    This function interfaces with a pre-trained ONNX model that implements
    the PrISM (Programmable Interactions in Spin Models) architecture to
    generate optimized control parameters.
    
    Args:
        jij_matrix (np.ndarray): The coupling matrix (Jij)
        onnx_model_path (str, optional): Path to the ONNX model file
            
    Returns:
        dict: Optimized parameters including:
            - rabi_frequencies (np.ndarray): The optimized Rabi frequencies
            - predicted_fidelity (float): The predicted fidelity of the optimization
            
    Raises:
        ValueError: If the coupling matrix is not valid or the ONNX model is not found
    """
    if jij_matrix is None:
        raise ValueError("Coupling matrix is None, cannot optimize parameters")
    
    try:
        # Import onnxruntime within the function to avoid dependency errors
        import onnxruntime as ort
        
        # Load the ONNX model
        if onnx_model_path is None:
            # Use default model path
            onnx_model_path = "models/prism_optimizer.onnx"
        
        # Create ONNX inference session
        session = ort.InferenceSession(onnx_model_path)
        
        # Prepare input
        # The PrISM model expects the upper triangular part of the Jij matrix
        input_name = session.get_inputs()[0].name
        
        # Vectorize the Jij matrix (extract upper triangular part)
        n = jij_matrix.shape[0]
        jij_vector = []
        for i in range(n):
            for j in range(i+1, n):
                jij_vector.append(jij_matrix[i, j])
        
        # Convert to numpy array and ensure correct data type
        jij_vector = np.array(jij_vector, dtype=np.float32)
        
        # Run inference
        results = session.run(None, {input_name: [jij_vector]})
        
        # Process output based on the PrISM model structure
        # The model outputs the Rabi frequencies and predicted fidelity
        rabi_frequencies = results[0][0]  # First output is the encoded parameters
        predicted_fidelity = results[1][0][0] if len(results) > 1 else 0.0  # Second output is fidelity
        
        return {
            "rabi_frequencies": rabi_frequencies,
            "predicted_fidelity": predicted_fidelity
        }
        
    except ImportError:
        raise ValueError("onnxruntime package is required for optimization")
    except Exception as e:
        raise ValueError(f"Error optimizing parameters: {str(e)}")