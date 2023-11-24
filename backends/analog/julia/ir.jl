using Configurations


@option struct ComplexFloat
    real::Float64
    imag::Float64
end

function complexf64_to_complexfloat(cf::ComplexF64)
    return ComplexFloat(reim(cf)...)
end


@option struct Operator
    coefficient::Union{Int, Float64, ComplexFloat} = 1.0
    pauli::Vector{String} = []
    ladder::Vector{Vector{Int}} = []
end


@option struct Dissipation
    jumps::Union{Nothing, Int} = nothing
end


@option struct AnalogGate
    duration::Float64
    hamiltonian::Vector{Operator} = []
    dissipation::Vector{Dissipation} = []
end


@option struct Evolve
    key::String = "evolve"
    gate::Union{AnalogGate, String}
end


@option struct Initialize
    key::String = "initialize"
end


@option struct Measure
    key::String = "measure"
end


Statement = Union{Initialize, Evolve, Measure}


@option struct AnalogCircuit
    qreg::Vector{Int}
    qmode::Vector{Int}

    definitions::Vector{Tuple{String, AnalogGate}} = []
    sequence::Vector{Statement} = []

    n_qreg::Maybe{Int} = nothing
    n_qmode::Maybe{Int} = nothing
 end





