import numpy as np

########################################################################################


def random_hexcolor():
    return "#{:02X}{:02X}{:02X}".format(*np.random.randint(0, 255, 3))
