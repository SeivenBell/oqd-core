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





