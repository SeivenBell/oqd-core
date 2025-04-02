from oqd_core.interface.analog import PauliX, AnalogGate, AnalogCircuit
from oqd_core.compiler.analog.passes import analog_operator_canonicalization
from oqd_compiler_infrastructure import RewriteRule, Post
from oqd_core.compiler.analog.passes.analysis import analysis_term_index
from oqd_core.compiler.math.passes import evaluate_math_expr

class XXGateAnalyzer(RewriteRule):
    """
    Rule to identify XX Hamiltonian terms and their weights with detailed logging.
    """
    def __init__(self):
        super().__init__()
        self.xx_gates = []
        self.xx_weights = []
        self.current_gate = None
        print("\n[INIT] Created new XXGateAnalyzer instance")
        print("    - xx_gates list initialized: []")
        print("    - xx_weights list initialized: []")
        print("    - current_gate initialized: None")
        
    def map_AnalogGate(self, model):
        """Track the current gate being analyzed"""
        print("\n[GATE] Entering a new AnalogGate")
        print(f"    - Gate ID: {id(model)}")
        print(f"    - Has hamiltonian: {hasattr(model, 'hamiltonian')}")
        
        # Update current_gate
        self.current_gate = model
        print(f"    - Updated current_gate to: {id(self.current_gate)}")
        
    def map_OperatorScalarMul(self, model):
        """Identify XX patterns with their weights"""
        print("\n[SCALAR] Processing an OperatorScalarMul")
        print(f"    - Operator type: {type(model.op).__name__}")
        
        # Get and print term indices
        term_indices = analysis_term_index(model.op)
        print(f"    - Term indices: {term_indices}")
        
        # Check pattern conditions
        print("\n[PATTERN] Checking for XX pattern:")
        has_indices = bool(term_indices)
        print(f"    - Has term indices: {has_indices}")
        
        if has_indices:
            correct_length = len(term_indices[0]) == 2
            print(f"    - Has exactly 2 operators: {correct_length}")
            
            if correct_length:
                is_xx_pattern = term_indices[0] == [1, 1]
                print(f"    - Is XX pattern [1,1]: {is_xx_pattern}")
                
                # Process XX pattern
                if is_xx_pattern:
                    print("\n[MATCH] Found XX pattern!")
                    
                    try:
                        # Try to evaluate the weight
                        print("    - Attempting to evaluate expression...")
                        weight = evaluate_math_expr(model.expr)
                        print(f"    - Evaluated weight: {weight}")
                        
                        # Record the findings
                        self.xx_gates.append(self.current_gate)
                        self.xx_weights.append(weight)
                        print(f"    - Added gate {id(self.current_gate)} with weight {weight}")
                        print(f"    - Current xx_gates count: {len(self.xx_gates)}")
                        
                    except (TypeError, ValueError) as e:
                        # Handle evaluation errors
                        print(f"    - ERROR: Could not evaluate expression: {e}")
            else:
                print("    - Not checking XX pattern as length is incorrect")
        else:
            print("    - Not checking XX pattern as no term indices present")

def analyze_xx_gates(circuit):
    """
    Analyze a circuit to find XX gates and their weights with detailed logging.
    """
    print("\n" + "="*80)
    print("STARTING XX GATE ANALYSIS")
    print("="*80)
    
    # Create and apply the analyzer
    print("\n[START] Creating analyzer instance")
    analyzer = XXGateAnalyzer()
    
    print("\n[TRAVERSAL] Starting Post-order traversal of circuit")
    print(f"    - Circuit has {len(circuit.sequence)} statements")
    Post(analyzer)(circuit)
    print("\n[TRAVERSAL] Completed Post-order traversal")
    
    # Summarize findings
    print("\n[RESULTS] Analysis complete")
    print(f"    - Found {len(analyzer.xx_gates)} XX gates")
    
    for i, (gate, weight) in enumerate(zip(analyzer.xx_gates, analyzer.xx_weights)):
        print(f"    - Gate {i+1}: ID {id(gate)}, Weight {weight}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    
    return analyzer.xx_gates, analyzer.xx_weights

def safe_describe_hamiltonian(hamiltonian):
    """Safely describe a Hamiltonian without using PrintOperator"""
    return f"{type(hamiltonian).__name__} object at {id(hamiltonian)}"

def test_xx_gate_analysis():
    """Test the XX gate analyzer with detailed logging"""
    print("\n" + "="*80)
    print("STARTING TEST SCRIPT")
    print("="*80)
    
    # Create basic operators
    print("\n[SETUP] Creating Pauli X operator")
    X = PauliX()
    print(f"    - Created operator: {X.__class__.__name__}")
    
    # Create gates with different coupling strengths
    print("\n[SETUP] Creating gates with different coupling strengths")
    xx_gates = [
        AnalogGate(hamiltonian=0.5 * (X @ X)),  # Weight 0.5
        AnalogGate(hamiltonian=1.0 * (X @ X)),  # Weight 1.0
        AnalogGate(hamiltonian=2.0 * (X @ X)),  # Weight 2.0
        AnalogGate(hamiltonian=3.5 * (X @ X)),  # Weight 3.5
    ]
    
    for i, gate in enumerate(xx_gates):
        print(f"    - Gate {i+1}: {safe_describe_hamiltonian(gate.hamiltonian)}")
    
    # Create circuit
    print("\n[SETUP] Creating circuit")
    circuit = AnalogCircuit()
    print(f"    - Created empty circuit: {circuit.__class__.__name__}")
    
    # Add gates to circuit
    print("\n[SETUP] Adding gates to circuit")
    for i, gate in enumerate(xx_gates):
        circuit.evolve(gate, 1.0)
        print(f"    - Added gate {i+1} with duration 1.0")
    
    print(f"    - Circuit now has {len(circuit.sequence)} statements")
    
    # Canonicalize the circuit
    print("\n" + "="*80)
    print("CANONICALIZING CIRCUIT")
    print("="*80)
    
    for i, statement in enumerate(circuit.sequence):
        if hasattr(statement, 'gate') and isinstance(statement.gate, AnalogGate):
            print(f"\n[CANON] Canonicalizing gate {i+1}")
            
            # Show before canonicalization
            before = safe_describe_hamiltonian(statement.gate.hamiltonian)
            print(f"    - Before: {before}")
            
            # Perform canonicalization
            statement.gate.hamiltonian = analog_operator_canonicalization(
                statement.gate.hamiltonian)
                
            # Show after canonicalization
            after = safe_describe_hamiltonian(statement.gate.hamiltonian)
            print(f"    - After: {after}")
    
    print("\n" + "="*80)
    print("RUNNING ANALYSIS")
    print("="*80)
    
    # Analyze the circuit
    found_gates, weights = analyze_xx_gates(circuit)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    print(f"\nFound {len(found_gates)} XX gates with weights:")
    for i, weight in enumerate(weights):
        print(f"Gate {i+1}: Weight = {weight}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_xx_gate_analysis()
    
    
    
# pytest, XY, II 