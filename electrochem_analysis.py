"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
import electrochem_data as echem_data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


class Curve:
    """
    Base class to plot data from multiple data file objects
    """
    def __init__(self, data_dir, file_type, info_path):
        self.dir = data_dir
        # keys = list(input.names.keys())
        # columns = pd.MultiIndex.from_product([[input.names[keys[0]]],
        #                                       [input.names[keys[1]]]])
        # self.variable = pd.DataFrame(input.values, columns=columns)
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

        # Create list of data file objects
        self.data_objects = []
        for name in self.data_file_names:
            path = os.path.join(data_dir, name)
            self.data_objects.append(echem_data.DataFile(path, file_type))

    def __getitem__(self, key):
        return self.data_objects[key]

    def mean_values(self, name='', points=0):
        mean_values = []
        file_names = []
        if name:
            for item in self.data_objects:
                mean_values.append(item[name].iloc[-points:].mean())
                file_names.append(os.path.split(item.path)[1].split('.')[0])
            mean_df = pd.concat(mean_values, axis=1).T
            mean_df.columns = pd.MultiIndex.from_tuples([(name,
                                                          mean_df.columns[0])])
        else:
            for item in self.data_objects:
                mean_values.append(item.data.iloc[-points:].mean())
                file_names.append(os.path.split(item.path)[1].split('.')[0])
            mean_df = pd.concat(mean_values, axis=1).T
        key = self.variable.data.keys()[0]
        mean_df[key] = file_names
        return self.variable.data.merge(mean_df)

    def plot_means(self, x_name, y_name, points=0):
        df = self.mean_values(y_name, points)
        fig = plt.figure(dpi=150)
        ax = df.plot(x_name, y_name)
        plt.tight_layout()
        plt.legend(fontsize='x-small')
        #plt.ylim((0, ymax))
        #plt.yticks(np.arange(0, ymax, step=1))
        #plt.xlabel('$x$ / mm')
        #plt.ylabel('$v_y$ / mm/s')
        #plt.xlim((x_axis_meas[0] * m_to_mm, x_axis_meas[1] * m_to_mm))
        #plt.ylim((0,0.015))
        #xticks = np.arange(0, 15.1, 1)
        #plt.xticks(xticks, minor=False)

        legend = plt.legend(loc='center right', bbox_to_anchor=(1.6, 0.5))
        legend.get_frame().set_linewidth(0.75)
        legend.get_frame().set_edgecolor('black')
        plt.grid('on')
        plt.savefig(os.path.join(self.dir, 'plot.png'),
                    bbox_inches='tight')
        return fig

