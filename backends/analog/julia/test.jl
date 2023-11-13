using JSON
using QuantumOptics

include("ir.jl")
include("task.jl")
include("quantumoptics.jl")


circ = AnalogCircuit(
    sequence=[
        AnalogGate(
            duration=1.0,
            unitary=[Operator(coefficient=1.0, qreg=["x", "x", "x", "x"], qmode=[])]
        )
    ],
    n_qreg = 1,
    n_qmode = 0
)

ee_vn = EntanglementEntropyVN(qreg=[0, 1], qmode=[])


args = TaskArgsAnalog(
    n_shots=10, fock_cutoff=2, dt=0.1,
    metrics=Dict(
        "ee_vn" => ee_vn,
    ),
)
task = Task(program=circ, args=args)

println(circ)
result = evolve(task);
println(result)