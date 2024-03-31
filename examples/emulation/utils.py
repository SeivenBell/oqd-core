import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
colors = sns.color_palette(palette="Set2", n_colors=10)

def _get_probabilities(state: list):
    probabililities = []
    for x in state:
        probabililities.append(np.sqrt(x.real**2 + x.imag**2)**2)
    return probabililities

def _get_amplitude(state: list, componenet = 'real'):
    amplitudes = []
    for x in state:
        if componenet == 'real':
            amplitudes.append(x.real)
        elif componenet == 'imag':
            amplitudes.append(x.imag)
        else:
            KeyError
    return amplitudes


def _generate_complete_dictionary(input_dict):

    n = len(list(input_dict.keys())[0])

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

def plot_metrics_counts(results, experiment_name, plot_directory = 'examples/emulation/plots/'):

    fig, axs = plt.subplots(3, 1, figsize=[8, 8])

    ax = axs[0]
    for k, (name, obs) in enumerate(results.metrics.items()):
        ax.plot(results.times, obs, label=f"$<{name}>$", color=colors[k])
    ax.legend()
    ax.set(xlabel="Time", ylabel="Expectation value")

    ax = axs[1]
    full_counts = _generate_complete_dictionary(results.counts)
    x = list(full_counts.keys())
    
    ax.bar(x=x, height=_get_probabilities(state = results.state), color=colors[2])
    ax.set(xlabel="Basis state", ylabel="Probability")


    ax = axs[2]
    counts = list(full_counts.values())

    ax.bar(x=x, height=counts, color=colors[3])
    ax.set(xlabel="Basis state", ylabel="Number of samples")

    ax = axs[3]
    ax.bar(x=x, height=_get_amplitude(state = results.state, componenet = 'real'), color=colors[5], label = 'Real component')
    ax.bar(x=x, height=_get_amplitude(state = results.state, componenet = 'imag'), color=colors[7], label = 'Imaginary component')
    plt.legend()
    ax.set(xlabel="Basis state", ylabel="Amplitude")

    fig.tight_layout()

    if not os.path.exists(plot_directory):
        os.makedirs(plot_directory)

    dirname = plot_directory + experiment_name
    plt.savefig(dirname)
