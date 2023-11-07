using Configurations
using JSON


# @option struct Operator
#     coefficient::Int = 1
#     qreg::Array{Int} = []
#     qmode::Array{Int} = []
#  end
#
#  @option struct Dissipation
#     jumps::Array{Int} = []
#  end

 @option struct AnalogGate
    duration::Int = 1
#     unitary::Array{Operator} = []
#     dissipation::Array{Dissipation} = []
 end

@option struct AnalogCircuit
#     definitions::Array{Int} = []
#     registers::Array{Int} = []
    sequence::Array{AnalogGate} = []
    n_qreg::Int = 0

#     n_qreg::Int = nothing
#     n_qmode::Int = nothing
 end


function test_analog_circuit(circ_json)
    println(AnalogCircuit())
#     println(circ_json)
    d = JSON.parse(circ_json);
    println(d)
#     aa = from_dict(AnalogCircuit, d);
#     println(aa)

#     for op in circ.sequence
#         println(op)
#     end
#
#     d = JSON.json(to_dict(circ))
end

# print(test_analog_circuit())
# println(AnalogGate())