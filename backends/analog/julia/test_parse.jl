# using JSON
using JSON3
using QuantumOptics
using Plots 
using Configurations

include("ir.jl")
include("task.jl")
# include("quantumoptics.jl")


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

# ee_vn = 10
# z = 1.0

metrics=Dict(
    "ee_vn" => ee_vn,
    "z" => z
)

args = TaskArgsAnalog(
    n_shots=10, fock_cutoff=2, dt=0.01,
    metrics=metrics,
)
task = Task(program=circ, args=args)

d = to_dict(task)
println(d)

json_string = JSON3.write(d)
# json_string = JSON.json(d)
# println(json_string)

d1 = JSON3.read(json_string);
# d1 = JSON.parse(json_string);
println(d1)

task_parse = from_dict(Task, d)
println(task_parse)


task_parse1 = JSON3.read(json_string, Task);
println(task_parse1)