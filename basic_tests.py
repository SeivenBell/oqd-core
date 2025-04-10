# xx_canonicalization_test.py
from rich import print as rprint
from pprint import pformat
import numpy as np

from oqd_core.interface.analog import (
    PauliX, PauliY, PauliZ, PauliI, 
    OperatorKron, OperatorAdd, OperatorScalarMul, OperatorSub,
    AnalogGate
)
from oqd_core.interface.math import MathNum, MathVar
from oqd_core.compiler.analog.passes import analog_operator_canonicalization

def print_operator_structure(op, label="", indent=0):
    """Print the structure of an operator using rich formatting."""
    if label:
        rprint(f"[bold green]{label}[/bold green]")
    
    # Convert the operator to a formatted dictionary structure
    def get_structure(o):
        result = {"type": o.__class__.__name__}
        
        # Handle different operator types
        if hasattr(o, "op1") and hasattr(o, "op2"):
            result["op1"] = get_structure(o.op1)
            result["op2"] = get_structure(o.op2)
        elif hasattr(o, "op") and hasattr(o, "expr"):
            result["op"] = get_structure(o.op)
            result["expr"] = {"type": o.expr.__class__.__name__}
            if isinstance(o.expr, MathNum):
                result["expr"]["value"] = o.expr.value
        
        return result
    
    # Print the structured representation
    rprint(pformat(get_structure(op), indent=indent))

# Helper function to create a multi-qubit operator
def create_term(op_positions, n_qubits, op_type=PauliX):
    """
    Create a term where specific positions have the operation type specified,
    and the rest have identity operators.
    
    Args:
        op_positions: List of positions where op_type should be placed
        n_qubits: Total number of qubits
        op_type: Type of operator to place (default PauliX)
        
    Returns:
        A Kronecker product operator
    """
    ops = [op_type() if i in op_positions else PauliI() for i in range(n_qubits)]
    term = ops[0]
    for op in ops[1:]:
        term = term @ op
    return term

# Define shortcuts
X, Y, Z, I = PauliX(), PauliY(), PauliZ(), PauliI()

print("\n" + "="*30 + " TEST CASES " + "="*30 + "\n")

# Test Case 1: Simple 2-qubit XX gate
print("\n" + "-"*20 + " Case 1: Simple 2-qubit XX gate " + "-"*20)
op1 = X @ X
print_operator_structure(op1, "Before canonicalization:")
canonical_op1 = analog_operator_canonicalization(op1)
print_operator_structure(canonical_op1, "After canonicalization:")

# Test Case 2: 3-qubit system with XX gate on qubits 0 and 2
print("\n" + "-"*20 + " Case 2: 3-qubit system with XX gate on qubits 0 and 2 " + "-"*20)
op2 = X @ I @ X
print_operator_structure(op2, "Before canonicalization:")
canonical_op2 = analog_operator_canonicalization(op2)
print_operator_structure(canonical_op2, "After canonicalization:")

# Test Case 3: 4-qubit system with multiple XX terms
print("\n" + "-"*20 + " Case 3: 4-qubit system with multiple XX terms " + "-"*20)
n_qubits = 4
term1 = create_term([0, 1], n_qubits)  # X_0 ⊗ X_1 ⊗ I_2 ⊗ I_3
term2 = create_term([1, 2], n_qubits)  # I_0 ⊗ X_1 ⊗ X_2 ⊗ I_3
term3 = create_term([0, 3], n_qubits)  # X_0 ⊗ I_1 ⊗ I_2 ⊗ X_3
op3 = term1 + term2 + term3
print_operator_structure(op3, "Before canonicalization:")
canonical_op3 = analog_operator_canonicalization(op3)
print_operator_structure(canonical_op3, "After canonicalization:")

# Test Case 4: 4-qubit system with weighted terms
print("\n" + "-"*20 + " Case 4: 4-qubit system with weighted terms " + "-"*20)
op4 = 1.0 * create_term([0, 1], n_qubits) + 2.0 * create_term([1, 2], n_qubits) + 0.5 * create_term([2, 3], n_qubits)
print_operator_structure(op4, "Before canonicalization:")
canonical_op4 = analog_operator_canonicalization(op4)
print_operator_structure(canonical_op4, "After canonicalization:")

# Test Case 5: Term with adjacent X operators
print("\n" + "-"*20 + " Case 5: Term with adjacent X operators " + "-"*20)
op5 = create_term([0, 1], 4)  # X_0 ⊗ X_1 ⊗ I_2 ⊗ I_3
print_operator_structure(op5, "Before canonicalization:")
canonical_op5 = analog_operator_canonicalization(op5)
print_operator_structure(canonical_op5, "After canonicalization:")

# Test Case 6: Term with non-adjacent X operators
print("\n" + "-"*20 + " Case 6: Term with non-adjacent X operators " + "-"*20)
op6 = create_term([0, 3], 4)  # X_0 ⊗ I_1 ⊗ I_2 ⊗ X_3
print_operator_structure(op6, "Before canonicalization:")
canonical_op6 = analog_operator_canonicalization(op6)
print_operator_structure(canonical_op6, "After canonicalization:")

# Test Case 7: Term with mixed operator types (should be incompatible)
print("\n" + "-"*20 + " Case 7: Term with mixed operator types " + "-"*20)
op7 = X @ Y @ I @ Z
print_operator_structure(op7, "Before canonicalization:")
canonical_op7 = analog_operator_canonicalization(op7)
print_operator_structure(canonical_op7, "After canonicalization:")

# Test Case 8: Large system (8 qubits) with multiple interactions
print("\n" + "-"*20 + " Case 8: Large system (8 qubits) " + "-"*20)
n_qubits = 8
op8 = (
    create_term([0, 1], n_qubits) + 
    create_term([1, 2], n_qubits) + 
    create_term([2, 3], n_qubits) +
    create_term([4, 5], n_qubits) +
    create_term([6, 7], n_qubits) +
    create_term([0, 7], n_qubits)
)
print_operator_structure(op8, "Before canonicalization (top-level only):")
canonical_op8 = analog_operator_canonicalization(op8)
print_operator_structure(canonical_op8, "After canonicalization (top-level only):")

# Test Case 9: More complex expression with subtraction
print("\n" + "-"*20 + " Case 9: Complex expression with subtraction " + "-"*20)
op9 = create_term([0, 1], 4) - 0.5 * create_term([2, 3], 4)
print_operator_structure(op9, "Before canonicalization:")
canonical_op9 = analog_operator_canonicalization(op9)
print_operator_structure(canonical_op9, "After canonicalization:")

# Test Case 10: AnalogGate wrapping
print("\n" + "-"*20 + " Case 10: AnalogGate wrapping " + "-"*20)
op10 = AnalogGate(hamiltonian=create_term([0, 2], 3))
print_operator_structure(op10.hamiltonian, "Before canonicalization:")
op10.hamiltonian = analog_operator_canonicalization(op10.hamiltonian)
print_operator_structure(op10.hamiltonian, "After canonicalization:")

print("\n" + "="*30 + " ANALYZING PATTERNS " + "="*30 + "\n")

# Let's check if we can reliably extract the qubit indices
print("\nAnalyzing Patterns in Canonicalized Operators:")

def identify_xx_pattern(op, indent=0):
    """
    Attempt to identify XX patterns in a canonicalized operator.
    This is a simplified version of what our analyzer would need to do.
    """
    indent_str = "  " * indent
    
    if isinstance(op, OperatorScalarMul):
        # Extract coefficient
        coef = "unknown"
        if isinstance(op.expr, MathNum):
            coef = op.expr.value
        
        print(f"{indent_str}OperatorScalarMul with coefficient: {coef}")
        identify_xx_pattern(op.op, indent + 1)
        
    elif isinstance(op, OperatorKron):
        # Check if this is a multi-qubit operator with X operators
        x_positions = []
        
        def find_x_positions(o, current_position=0):
            """Recursively find positions of X operators."""
            if isinstance(o, PauliX):
                x_positions.append(current_position)
                return
            if isinstance(o, PauliI):
                return
            if isinstance(o, OperatorKron):
                find_x_positions(o.op1, current_position)
                find_x_positions(o.op2, current_position + 1)
        
        # This is a simplified approach and won't work for all cases
        find_x_positions(op)
        
        if len(x_positions) == 2:
            print(f"{indent_str}Found XX interaction between qubits {x_positions[0]} and {x_positions[1]}")
        else:
            print(f"{indent_str}Found X operators at positions: {x_positions}")
            
    elif isinstance(op, OperatorAdd):
        print(f"{indent_str}OperatorAdd with multiple terms:")
        identify_xx_pattern(op.op1, indent + 1)
        identify_xx_pattern(op.op2, indent + 1)
        
    else:
        print(f"{indent_str}Unrecognized pattern: {op.__class__.__name__}")

# Analyze a few of our canonicalized operators
print("\nAnalyzing Case 2 (3-qubit system):")
identify_xx_pattern(canonical_op2)

print("\nAnalyzing Case 3 (4-qubit system with multiple terms):")
identify_xx_pattern(canonical_op3)

print("\nAnalyzing Case 4 (Weighted terms):")
identify_xx_pattern(canonical_op4)

print("\nAnalyzing Case 6 (Non-adjacent X operators):")
identify_xx_pattern(canonical_op6)