import pathlib
import warnings
import os
import copy
import datetime
import json
import string
import random
import yaml

from numpy import ndarray

from matplotlib.figure import Figure

import pandas as pd
from pandas import DataFrame

from typing import Optional, Any


def current_time():
    """
    Returns current date and time in a consistent format, used for monitoring long-running measurements

    Returns:
        (str): current date and time
    """
    return datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")


class IO:
    r"""
    The IO class encapsulates all saving/loading features of data, figures, etc.
    """

    default_path = (
        pathlib.Path(os.path.expanduser("~")).joinpath("data").joinpath("oqd")
    )

    def __init__(
        self,
        path=None,
        folder="",
        include_date=False,
        include_time=False,
        include_id=False,
        verbose=True,
    ):
        """
        Args:
            path (Optional[str]): The parent folder.
            folder (str): The main, descriptive folder name.
            include_date (bool): If True, add the date to the front of the path. Otherwise, do not add the date
            include_time (bool): If True, add the time to the front of the path. Otherwise, do not add the time
            include_id (bool): If True, add a random string of characters to the end of the path. Otherwise, do not
            verbose (bool): If True, will print out the path of each saved/loaded file.

        Returns:
            (IO): A new IO class instance

        """
        if path is None:
            path = self.default_path

        if type(path) is str:
            path = pathlib.Path(path)

        date = datetime.date.today().isoformat()
        time = datetime.datetime.now().strftime("%H-%M-%S")
        if not folder:  # if empty string
            warnings.warn(
                "No folder entered. Saving to a folder with a unique identifier"
            )
            include_data, include_id, verbose = True, True, True

        # build the full folder name with date, time, and uuid, if selected
        _str = ""
        if include_date:
            _str = _str + date + "_"
        if include_time:
            _str = _str + time + "_"

        _str = _str + folder

        if include_id:
            _str = (
                _str + "_" + "".join(random.choice(string.hexdigits) for _ in range(4))
            )

        self.path = path.joinpath(_str)
        self.verbose = verbose
        return

    def subpath(self, subfolder: str):
        cls = copy.deepcopy(self)
        cls.path = cls.path.joinpath(subfolder)
        return cls

    def save_json(self, variable, filename):
        """
        Save serialized python object into a json file at filename

        Args:
            variable (object): the object to save
            filename (str): name of the file to which variable should be saved
        """
        full_path = self.path.joinpath(filename)
        os.makedirs(full_path.parent, exist_ok=True)
        self._save_json(variable, full_path)
        if self.verbose:
            print(f"{current_time()} | Saved to {full_path} successfully.")

    def load_json(self, filename):
        """
        Load serialized python object from json

        Args:
            filename (str): name of the file from which we are loading the object

        Returns:
            (Any): the loaded object data
        """
        full_path = self.path.joinpath(filename)
        file = self._load_json(full_path)
        if self.verbose:
            print(f"{current_time()} | Loaded from {full_path} successfully.")
        return file

    def save_txt(self, variable, filename):
        """
        Save serialized python object into a text file at filename

        Args:
            variable (object): the object to save
            filename (str): name of the file to which variable should be saved
        """
        full_path = self.path.joinpath(filename)
        os.makedirs(full_path.parent, exist_ok=True)
        self._save_txt(variable, full_path)
        if self.verbose:
            print(f"{current_time()} | Saved to {full_path} successfully.")

    def load_txt(self, filename):
        """
        Load serialized python object from text file

        Args:
            filename (str): name of the file from which we are loading the object

        Returns:
            (Any): the loaded object data
        """
        full_path = self.path.joinpath(filename)
        file = self._load_txt(full_path)
        if self.verbose:
            print(f"{current_time()} | Loaded from {full_path} successfully.")
        return file

    def save_dataframe(self, df, filename):
        """
        Save a panda dataframe object to pkl

        Args:
            df (DataFrame): data contained in a dataframe
            filename (str): file to which data should be saved
        """
        ext = ".pkl"
        full_path = self.path.joinpath(filename + ext)
        os.makedirs(full_path.parent, exist_ok=True)
        # df.to_csv(str(full_path), sep=",", index=False, header=True)
        df.to_pickle(str(full_path))
        if self.verbose:
            print(f"{current_time()} | Saved to {full_path} successfully.")

    def load_dataframe(self, filename):
        """
        Load panda dataframe object from pkl

        Args:
            filename (str): name of the file from which data should be loaded

        Returns:
            (DataFrame): dataframe data
        """
        import pandas as pd

        ext = ".pkl"
        full_path = self.path.joinpath(filename + ext)
        # df = pd.read_csv(str(full_path), sep=",", header=0)
        df = pd.read_pickle(str(full_path))
        if self.verbose:
            print(f"{current_time()} | Loaded from {full_path} successfully.")
        return df

    def save_figure(self, fig, filename):
        """
        Save a figure (image datatype can be specified as part of filename)

        Args:
            fig (Figure): the figure containing the figure to save
            filename (str): the filename to which we save a figure
        """
        full_path = self.path.joinpath(filename)
        os.makedirs(full_path.parent, exist_ok=True)
        fig.savefig(full_path, dpi=300, bbox_inches="tight")
        if self.verbose:
            print(f"{current_time()} | Saved figure to {full_path} successfully.")

    def save_np_array(self, np_arr, filename):
        """
        Save numpy array to a text document

        Args:
            np_arr (ndarray): the array which we are saving
            filename (str): name of the text file to which we want to save the numpy array
        """
        import numpy as np

        full_path = self.path.joinpath(filename)
        os.makedirs(full_path.parent, exist_ok=True)
        np.savetxt(str(full_path), np_arr)
        if self.verbose:
            print(f"{current_time()} | Saved to {full_path} successfully.")

    def load_np_array(self, filename, complex_vals=False):
        """
        Loads numpy array from a text document

        Args:
            filename (str): name of the text file from which we want to load the numpy array
            complex_vals (bool): True if we expect the numpy array to be complex, False otherwise

        Returns:
            (ndarray): numpy array of data
        """
        import numpy as np

        full_path = self.path.joinpath(filename)
        file = np.loadtxt(
            str(full_path), dtype=np.complex if complex_vals else np.float
        )
        if self.verbose:
            print(f"{current_time()} | Loaded from {full_path} successfully.")
        return file

    def save_csv(self, df, filename):
        """
        Save a panda dataframe object to csv

        Args:
            df (DataFrame): data contained in a dataframe
            filename (str): file to which data should be saved
        """
        ext = ".csv"
        full_path = self.path.joinpath(filename + ext)
        os.makedirs(full_path.parent, exist_ok=True)
        df.to_csv(str(full_path), sep=",", index=False, header=True)
        if self.verbose:
            print(f"{current_time()} | Saved to {full_path} successfully.")

    def load_csv(self, filename):
        """
        Load panda dataframe object from csv

        Args:
            filename (str): name of the file from which data should be loaded

        Returns:
            (DataFrame): dataframe data
        """
        full_path = self.path.joinpath(filename)
        df = pd.read_csv(str(full_path), sep=",", header=0)
        if self.verbose:
            print(f"{current_time()} | Loaded from {full_path} successfully.")
        return df

    @staticmethod
    def _save_json(variable, path):
        """
        Helper method for saving to json files
        """
        with open(path, "w+") as json_file:
            json.dump(variable, json_file, indent=4)

    @staticmethod
    def _load_json(path):
        """
        Helper method for loading from json files
        """
        with open(path) as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def _save_txt(variable, path):
        """
        Helper method for saving to text files
        """
        with open(path, "w") as txt_file:
            txt_file.write(variable)

    @staticmethod
    def _load_txt(path):
        """
        Helper method for loading from text files
        """
        # with open(path) as json_file:
        #     data = json.load(json_file)
        # return data
        with open(path) as txt_file:
            txt_str = txt_file.read()
        return txt_str
