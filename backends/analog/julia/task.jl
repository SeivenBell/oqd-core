using Configurations

include("ir.jl")
include("metric.jl")



@option struct TaskArgsAnalog
    n_shots::Int = 1
    fock_cutoff::Int = 1
    dt::Float64 = 0.1
    metrics::Dict{String, Metric} = Dict()
end


@option mutable struct DataAnalog
    times::Vector{Float64} = []
    expect::Dict{String, Vector{Float64}} = Dict()
    state::Ket
end


@option mutable struct TaskResultAnalog
    counts::Dict{Int, Int} = Dict()
    times::Vector{Float64} = []
    state::Vector{ComplexF64}
    runtime::Float64
    metrics::Dict{String, Vector{Union{Int, Float64}}} = Dict()
end


@option struct Task
    program::AnalogCircuit
    args::TaskArgsAnalog
 end
