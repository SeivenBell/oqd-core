using Configurations

include("ir.jl")


@option struct Expectation
    operator::Vector{Operator}
end


@option struct EntanglementEntropyVN
    qreg::Vector{Int}
    qmode::Vector{Int}
end

Metric = Union{EntanglementEntropyVN, Expectation}