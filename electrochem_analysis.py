"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
import electrochem_data as echem_data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import input


class Curve:
    """
    Base class to plot data from multiple data file objects
    """
    def __init__(self, dir):
        self.dir = dir
        keys = list(input.names.keys())
        columns = pd.MultiIndex.from_product([[input.names[keys[0]]],
                                              [input.names[keys[1]]]],
                                             names=[keys[0], keys[1]])
        self.variable = pd.DataFrame(input.values, columns=columns)

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

    def mean_values(self, name='', points=0):
        mean_values = []
        if name:
            if points > 0:
                for item in self.data_objects:
                    mean_values.append(item[name].iloc[-points:].mean())
            else:
                for item in self.data_objects:
                    mean_values.append(item[name].mean())
        else:
            if points > 0:
                for item in self.data_objects:
                    mean_values.append(item.data.iloc[-points:].mean())
            else:
                for item in self.data_objects:
                    mean_values.append(item.data.mean())

        #mean_df = pd.concat(mean_values, axis=1).T
        #columns = pd.MultiIndex(levels=[[name], mean_df.columns])
        #Test
        return pd.concat(mean_values, axis=1).T

    def plot_means(self, name, x_series, points=0):
        y_series = self.mean_values(name, points)

        fig = plt.figure(dpi=150)
        plt.tight_layout()
        plt.plot(x, y, 'k-', linewidth=1, markersize=3, label="label")
        plt.legend(fontsize='x-small')
        #plt.ylim((0, ymax))
        #plt.yticks(np.arange(0, ymax, step=1))
        plt.xlabel('$x$ / mm')
        plt.ylabel('$v_y$ / mm/s')
        #plt.xlim((x_axis_meas[0] * m_to_mm, x_axis_meas[1] * m_to_mm))
        plt.ylim((0,0.015))
        xticks = np.arange(0, 15.1, 1)
        plt.xticks(xticks, minor=False)

        legend = plt.legend(loc='center right', bbox_to_anchor=(1.6, 0.5))
        legend.get_frame().set_linewidth(0.75)
        legend.get_frame().set_edgecolor('black')
        plt.grid('on')
        plt.savefig(os.path.join(self.dir, 'plot.png'),
                    bbox_inches='tight')
        return fig

