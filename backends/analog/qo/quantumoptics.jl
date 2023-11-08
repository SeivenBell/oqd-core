using JSON
using QuantumOptics

include("ir.jl")


_fock_cutoff = 3;

b = SpinBasis(1//2);
f = FockBasis(_fock_cutoff);

_map_qreg = Dict(
    "i" => identityoperator(b),
    "x" => sigmax(b),
    "y" => sigmay(b),
    "z" => sigmaz(b)
);

_map_qmode = Dict(
    0 => identityoperator(f),
    -1 => destroy(f),
    +1 => create(f),
);

function _map_operator_to_qo(operator::Operator)
    _hs = []
    if !isempty(operator.qreg)
        _h_qreg = [_map_qreg[qreg] for qreg in operator.qreg]
        _hs = vcat(_hs, _h_qreg);
    end
    if !isempty(operator.qreg)
        _h_qmode = [prod([_map_qmode[qmode_op] for qmode_op in mode]) for mode in operator.qmode]
        _hs = vcat(_hs, _h_qmode);
    end
    op = operator.coefficient * tensor(_hs...)
    return op
end



function convert(circ_json::String)
    d = JSON.parse(circ_json);
    circ = from_dict(AnalogCircuit, d);
    println(circ)
end

function run(circ_json::String)
    circ = convert(circ_json);
    return evolve(circ)
end

function evolve(circ::AnalogCircuit)
    
    dt = 0.1;

    state_qreg = [spinup(b) for qreg in 1:circ.n_qreg];
    state_qmode = [fockstate(f, 0) for qmode in 1:circ.n_qmode];
    psi = tensor(vcat(state_qreg, state_qmode)...);
    println("Intial state:   ", psi)

    for gate in circ.sequence
        println("running the gate", gate)
        tspan = range(0, stop=gate.duration, step=dt)
        H = sum([_map_operator_to_qo(operator) for operator in gate.unitary])
        tout, psi_t = timeevolution.schroedinger(tspan, psi, H)
        println(psi_t)
    end

    return psi
end

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


println(circ)
evolve(circ)