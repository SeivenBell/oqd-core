using Configurations

include("ir.jl")
include("metric.jl")


@option struct TaskArgsAnalog
    n_shots::Int = 1
    fock_cutoff::Int = 1
    dt::Float64 = 0.1
    # metrics::Dict{String, Union{EntanglementEntropyVN, Expectation}} = Dict()
    metrics::Dict{String, Metric} = Dict()
    # metrics::Dict{String, Union{EntanglementEntropyVN, Float64}} = Dict()
end


@option mutable struct DataAnalog
    times::Vector{Float64} = []
    state::Ket
    metrics:: Dict{String, Vector{Union{Float64, Int64}}} = Dict()
end


@option mutable struct TaskResultAnalog
    counts::Dict{Int, Int} = Dict()
    times::Vector{Float64} = []
    state::Vector{ComplexF64} = []
    runtime::Float64 = 1.0
    metrics::Dict{String, Vector{Union{Int64, Float64}}} = Dict()
end


@option struct Task
    program::AnalogCircuit
    args::TaskArgsAnalog
 end
