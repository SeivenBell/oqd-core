using JSON
using QuantumOptics

include("ir.jl")
include("task.jl")



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
    runtime = @elapsed begin
        circ = task.program;
        args = task.args;

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


        # todo: change to Metrics, rather than operator
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
            op = operator.coefficient * tensor(_hs...);
            return op
        end

        function _sum_operators(operators::Vector{Operator})
            return sum([_map_operator_to_qo(operator) for operator in operators])
        end

        function _map_gate_to_qobj(gate::AnalogGate)
            return _sum_operators(gate.unitary)
        end

        function _map_metric(metric::Metric, circ::AnalogCircuit)
            if isa(metric, EntanglementEntropyVN)
                f = (t, psi) -> entanglement_entropy_vn(t, psi, metric.qreg, metric.qmode, circ.n_qreg, circ.n_qmode);
            elseif isa(metric, Expectation)
                f = (t, psi) -> expect(_sum_operators(metric.operator, psi));
            else
                println("Not a valid metric type.")
            end
            println("fmetric 1", typeof(f))
            return f
        end

        function _initialize()
            state_qreg = [spinup(b) for qreg in 1:circ.n_qreg];
            state_qmode = [fockstate(f, 0) for qmode in 1:circ.n_qmode];
            psi = tensor(vcat(state_qreg, state_qmode)...);
            return psi
        end

        psi = _initialize();
        println(args.metrics);
        fmetrics = Dict(key => _map_metric(metric, circ) for (key, metric) in args.metrics)

        data = DataAnalog(
            state=psi,
            metrics=Dict(key => [] for (key, metric) in args.metrics),
        );

        function fout(t, psi)
            data.state = psi;
            for (key, fmetric) in fmetrics
                push!(data.metrics[key], fmetric(t, psi));
            end
        end
        
        t0 = 0.0
        for gate in circ.sequence
            tspan = range(0, stop=gate.duration, step=args.dt);
            t0 = gate.duration
            append!(data.times, collect(tspan) .+ t0);
            
            H = _map_gate_to_qobj(gate);
            println("type of H", typeof(H))
            println("type of psi", typeof(psi))
            
            timeevolution.schroedinger(tspan, psi, H); #; fout=fout);
        end
    end

    result = TaskResultAnalog(
        # expect=data.expect,
        times=data.times,
        runtime=runtime,
        state=data.state.data,
        metrics=data.metrics,
    )

#     println(result);
    return JSON.json(to_dict(result))
end



function entanglement_entropy_vn(t, psi, qreg, qmode, n_qreg, n_qmode)
    rho = ptrace(psi, qreg + [n_qreg + m for m in qmode])
    return entropy_vn(rho)
end

