using QuantumOptics
using Configurations


@option struct Expectation
    operator::Vector{Int}
    qmode::Vector{Int}
end


@option struct EntanglementEntropyVN
    qreg::Vector{Int}
    qmode::Vector{Int}
end


Metric = Union{Expectation, EntanglementEntropyVN}


function entanglement_entropy_vn(t, psi)
    return
end