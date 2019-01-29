"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
import electrochem_data as echem_data
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np


class Curve:
    """
    Base class to plot data from multiple data file objects
    """
    def __init__(self, data_dir, file_type, info_path):
        self.dir = data_dir
        self.variable = echem_data.DataFile(info_path, 'Info')

        # Find files in directory
        file_names = os.listdir(data_dir)
        # Loop over list and find most common file extension
        ext_dict = {}
        for name in file_names:
            ext = name.rsplit('.')[1]
            ext_dict.setdefault(ext, 0)
            ext_dict[ext] += 1
        file_ext = max(ext_dict, key=ext_dict.get)

        # List only containing data file names
        self.data_file_names = []
        for name in file_names:
            if name.endswith(file_ext):
                self.data_file_names.append(name)

        # Set variable data frame in variable data object
        self.variable.set_vars_from_file_names(self.data_file_names)

        # Create list of data file objects
        self.data_objects = []
        for name in self.data_file_names:
            path = os.path.join(data_dir, name)
            self.data_objects.append(echem_data.DataFile(path, file_type))

        # Write variable data into data objects
        var_data = self.variable.data
        var_values = []
        for item in self.data_objects:
            item.variable = {}
            var_name = var_data.columns[1][0]
            item.variable['name'] = var_name
            item.variable['unit'] = var_data.columns[1][1]
            file_name = item.file_name
            value = float(var_data.loc[
                var_data['File Name']['-'] == file_name][var_name].iloc[0][0])
            item.variable['value'] = value
            var_values.append(value)

        # Sort data objects according to variable values
        self.data_objects = \
            [x for _, x in sorted(zip(var_values, self.data_objects))]

    def __getitem__(self, key):
        return self.data_objects[key]

    def mean_values(self, name='', points=0):
        mean_values = []
        file_names = []
        if name:
            for item in self.data_objects:
                mean_values.append(item[name].iloc[-points:].mean())
                file_names.append(item.file_name)
            mean_df = pd.concat(mean_values, axis=1).T
            mean_df.columns = pd.MultiIndex.from_tuples([(name,
                                                          mean_df.columns[0])])
        else:
            for item in self.data_objects:
                mean_values.append(item.data.iloc[-points:].mean())
                file_names.append(item.file_name)
            mean_df = pd.concat(mean_values, axis=1).T
        key = self.variable.data.keys()[0]
        mean_df[key] = file_names
        return self.variable.data.merge(mean_df)

    def plot_means(self, x_name, y_name, points=0):
        df = self.mean_values(y_name, points)
        ax = df.plot(x_name, y_name, style=['k.-'], markersize=10)
        x_unit = df[x_name].columns[0]
        ax.set_xlabel(x_name + ' / ' + x_unit)
        y_unit = df[y_name].columns[0]
        ax.set_ylabel(y_name + ' / ' + y_unit)
        ax.legend(loc='best')
        ax.grid(True)
        plt.savefig(os.path.join(self.dir, 'plot_mean_values.png'),
                    bbox_inches='tight')

    def plot_series(self, column_name,
                    start=0, stop=None, step=None):
        labels = []
        for item in self.data_objects:
            label = str(item.variable['value']) + ' ' \
                    + str(item.variable['unit'])
            labels.append(label)
        if stop and start >= stop:
            item = self.data_objects[0].data
            ax = item.iloc[start::step].plot('Time', column_name)
            for i in range(1, len(self.data_objects)):
                item = self.data_objects[i].data
                item.iloc[start::step].plot('Time', column_name, ax=ax)
        else:
            slicer = slice(start, stop, step)
            item = self.data_objects[0].data
            ax = item.iloc[slicer].plot('Time', column_name)
            for i in range(1, len(self.data_objects)):
                item = self.data_objects[i].data
                ax = item.iloc[slicer].plot('Time', column_name, ax=ax)
        x_unit = self.data_objects[0].data['Time'].columns[0]
        ax.set_xlabel('Time / '+x_unit)
        y_unit = self.data_objects[0].data[column_name].columns[0]
        ax.set_ylabel(column_name + ' / ' + y_unit)
        ax.legend(labels, loc='best')
        ax.grid(True)
        plt.savefig(os.path.join(self.dir, 'plot_time_series.png'),
                    bbox_inches='tight')


