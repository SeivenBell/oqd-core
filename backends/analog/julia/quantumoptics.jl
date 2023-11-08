using JSON
using QuantumOptics

include("ir.jl")


function convert(task_json::String)
    d = JSON.parse(task_json);
    task = from_dict(Task, d);
    return task
end

function run(task_json::String)
    task = convert(task_json);
    result = evolve(task);
    return result
end

function evolve(task::Task)
    circ = task.program;
    args = task.args;
    result = TaskResultAnalog()

    b = SpinBasis(1//2);
    f = FockBasis(args.fock_cutoff);

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

    state_qreg = [spinup(b) for qreg in 1:circ.n_qreg];
    state_qmode = [fockstate(f, 0) for qmode in 1:circ.n_qmode];
    psi = tensor(vcat(state_qreg, state_qmode)...);
    println("Intial state:   ", psi)

    for gate in circ.sequence
        tspan = range(0, stop=gate.duration, step=args.dt);
        H = sum([_map_operator_to_qo(operator) for operator in gate.unitary]);
        tout, psi_t = timeevolution.schroedinger(tspan, psi, H);
        result.times = tout;
    end
    println(result);
    return JSON.json(to_dict(result))
end
