import numpy as np

def amplitude(state: list):
    amplitudes = []
    for x in state:
        amplitudes.append(np.sqrt(x.real**2 + x.imag**2))
    return amplitudes

def generate_complete_dictionary(input_dict):

    n = len(list(input_dict.keys())[0])
    print(n)

    complete_dict = {}
    # Generate all possible binary strings of length n
    for i in range(2**n):
        binary_string = format(i, 'b').zfill(n)
        
        # Check if the binary string is already in the input dictionary
        if binary_string not in input_dict:
            complete_dict[binary_string] = 0

    # Add the keys from the input dictionary
    complete_dict.update(input_dict)
    
    return {k: complete_dict[k] for k in sorted(complete_dict)}
