using QuantumOptics
using Configurations

include("ir.jl")


@option struct Expectation
    operator::Vector{Operator}
end


@option struct EntanglementEntropyVN
    qreg::Vector{Int}
    qmode::Vector{Int}
end


Metric = Union{Expectation, EntanglementEntropyVN}


function entanglement_entropy_vn(t, psi)
    return
end