import numpy as np

########################################################################################


def random_hexcolor():
    """
    Generates a random hexstring color
    """
    return "#{:02X}{:02X}{:02X}".format(*np.random.randint(0, 255, 3))
