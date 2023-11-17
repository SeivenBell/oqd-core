using JSON
using QuantumOptics
using Plots 

include("ir.jl")
include("task.jl")
include("quantumoptics.jl")


circ = AnalogCircuit(
    sequence=[
        AnalogGate(
            duration=4.0,
            unitary=[Operator(coefficient=1.0, qreg=["x", "x"], qmode=[])]
        )
    ],
    n_qreg = 2,
    n_qmode = 0
)

ee_vn = EntanglementEntropyVN(qreg=[0], qmode=[])
z = Expectation(
    operator=[
        Operator(coefficient=0.5, qreg=["z", "i"], qmode=[]),
        Operator(coefficient=0.5, qreg=["i", "z"], qmode=[]),
    ]
)


args = TaskArgsAnalog(
    n_shots=10, fock_cutoff=2, dt=0.01,
    metrics=Dict(
        "ee_vn" => ee_vn,
        "z" => z,
    ),
)
task = Task(program=circ, args=args)

println(circ)
result = evolve(task);
println(result.metrics)
println(result.metrics["ee_vn"])
println(result.times)

p1 = plot(result.times, result.metrics["ee_vn"], xlabel="Time [arb.]", ylabel="S(ρ)", reuse=false)
display(p1)
p2 = plot(result.times, result.metrics["z"], xlabel="Time [arb.]", ylabel="<z>", reuse=false)
