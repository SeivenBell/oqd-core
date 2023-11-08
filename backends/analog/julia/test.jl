using JSON
using QuantumOptics

include("ir.jl")
include("quantumoptics.jl")


circ = AnalogCircuit(
    sequence=[
        AnalogGate(
            duration=1.0,
            unitary=[Operator(coefficient=1.0, qreg=["x"], qmode=[])]
        )
    ],
    n_qreg = 1,
    n_qmode = 0
)

args = TaskArgsAnalog(
    n_shots=10, fock_cutoff=2, dt=0.1,
    observables=Dict(
        "x" => Operator(coefficient=1.0, qreg=["x"], qmode=[]),
        "y" => Operator(coefficient=1.0, qreg=["y"], qmode=[]),
        "z" => Operator(coefficient=1.0, qreg=["z"], qmode=[]),
    ),
)
task = Task(program=circ, args=args)

println(circ)
result = evolve(task);
println(result)