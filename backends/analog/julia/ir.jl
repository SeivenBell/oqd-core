using Configurations


@option struct Operator
    coefficient::Union{Int, Float64} = 1.0
    qreg::Vector{String} = []
    qmode::Vector{Vector{Int}} = []
end


@option struct Dissipation
    jumps::Union{Nothing, Int} = nothing
end


@option struct AnalogGate
    duration::Union{Int, Float64, Nothing} = nothing
    unitary::Vector{Operator} = []
    dissipation::Vector{Dissipation} = []
end


@option struct Statement
    key::String
    assignment::Union{AnalogGate}
end


@option struct AnalogCircuit
    definitions::Vector{Int} = []
    registers::Vector{Int} = []
    sequence::Vector{AnalogGate} = []
    n_qreg::Union{Nothing, Int} = nothing
    n_qmode::Union{Nothing, Int} = nothing
 end


@option struct TaskArgsAnalog
    n_shots::Int = 1
    fock_cutoff::Int = 1
    observables::Dict{String, Operator} = Dict()
    dt::Float64 = 0.1
end


@option mutable struct DataAnalog
    times::Vector{Float64} = []
    expect::Dict{String, Vector{Float64}} = Dict()
    state::Ket
end


@option mutable struct TaskResultAnalog
    counts::Dict{Int, Int} = Dict()
    expect::Dict{String, Vector{Union{Int, Float64}}} = Dict()
    times::Vector{Float64} = []
    state::Vector{ComplexF64}
    runtime::Float64
end


@option struct Task
    program::AnalogCircuit
    args::TaskArgsAnalog
 end



