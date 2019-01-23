"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
import electrochem_data as echem_data


class Curve:
    """
    Base class to plot data from multiple data file objects
    """
    def __init__(self, dir):
        # Find files in directory
        file_names = os.listdir(dir)
        # Loop over list and find most common file extension
        ext_dict = {}
        for name in file_names:
            ext = name.rsplit('.')[1]
            ext_dict.setdefault(ext, 0)
            ext_dict[ext] += 1
        file_ext = max(ext_dict, key=ext_dict.get)

        # List only containing data file names
        data_file_names = []
        for name in file_names:
            if name.endswith(file_ext):
                data_file_names.append(name)

        # Create list of data file objects
        self.data_objects = []
        for name in data_file_names:
            path = os.path.join(dir, name)
            self.data_objects.append(echem_data.DataFile(path))

    def __getitem__(self, key):
        return self.data_objects[key]

    def mean_values(self, variable, points = 0):
        mean_values = []
        if points > 0:
            for item in self.data_objects:
                mean_values.append(item.data[-points:].mean()[variable])
        return mean_values
