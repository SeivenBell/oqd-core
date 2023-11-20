using Configurations

include("ir.jl")


@option "expectation" struct Expectation
    # type::Reflect
    operator::Vector{Operator}
end


@option "entanglement_entropy_vn" struct EntanglementEntropyVN
    # type::Reflect
    qreg::Vector{Int}
    qmode::Vector{Int}
end

Metric = Union{EntanglementEntropyVN, Expectation}