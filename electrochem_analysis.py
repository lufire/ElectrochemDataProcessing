"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
import electrochem_data as ea
import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle, islice


class Curve:
    """
    Base class to plot data from multiple data file objects
    """
    def __init__(self, base_dir, data_file_type, data_folder='Data'):
        self.data_folder = data_folder
        self.data_dir = os.path.join(base_dir, self.data_folder)
        self.work_dir = base_dir

        # Find files in directory
        file_names = os.listdir(self.data_dir)
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

        # Create variable object describing variation between data objects
        self.variable = ea.InfoFile(os.path.join(base_dir, 'info.txt'),
                                    names=self.data_file_names)

        # Create list of data file objects
        self.data_objects = []
        for name in self.data_file_names:
            path = os.path.join(self.data_dir, name)
            self.data_objects.append(ea.EChemDataFile(path,
                                                      data_file_type))

        # Write variable data into data objects
        var_data = self.variable.data
        var_values = []
        for item in self.data_objects:
            item.variable = {}
            var_name = var_data.columns[1]
            item.variable['name'] = var_name
            item.variable['unit'] = self.variable.units[var_name]
            file_name = item.file_name
            value = float(var_data.loc[
                var_data['File Name'] == file_name][var_name].iloc[0])
            item.variable['value'] = value
            var_values.append(value)

        # Sort data objects according to variable values
        self.data_objects = \
            [x for _, x in sorted(zip(var_values, self.data_objects))]

        # Initialize current density column in the DataFile objects
        self.calculate_current_density()

    def __getitem__(self, key):
        return self.data_objects[key]

    def mean_values(self, name='', points=0):
        mean_values = []
        file_names = []
        if name:
            for item in self.data_objects:
                mean_values.append(item[name].iloc[-points:].mean())
                file_names.append(item.file_name)
            mean_df = pd.DataFrame(mean_values)
            mean_df.columns = [name]
        else:
            for item in self.data_objects:
                mean_values.append(item.data.iloc[-points:].mean())
                file_names.append(item.file_name)
            mean_df = pd.concat(mean_values, axis=1).T
        key = self.variable.data.keys()[0]
        mean_df[key] = file_names
        return self.variable.data.merge(mean_df)

    def calculate_current_density(self, electrode_area=None):
        if not electrode_area:
            electrode_area = {}
            electrode_area['name'] = 'Electrode Surface Area'
            key = 'ELECTRODE SURFACE AREA'
            if key in self.variable.header:
                electrode_area['value'] = \
                    float(self.variable.header[key][0])
                electrode_area['unit'] = \
                    str(self.variable.header[key][1])
            else:
                electrode_area['value'] = float(input('Provide value for '
                                                      'electrode surface '
                                                      'area:'))
                electrode_area['unit'] = input('Provide unit for electrode '
                                               'surface area:')
        for item in self.data_objects:
            item.calculate_current_density(electrode_area)

    def plot_means(self, x_name, y_name, ax=None,
                   points=0, label=None, save_file=False):
        mean_df = self.mean_values(y_name, points)
        if x_name in self.variable.units:
            x_unit = self.variable.units[x_name]
        else:
            x_unit = self.data_objects[0].units[x_name]
        y_unit = self.data_objects[0].units[y_name]
        ax = mean_df.plot(x_name, y_name, ax=ax, markersize=10, legend=False)
        ax.set_xlabel(x_name + ' / $' + x_unit + '$')
        ax.set_ylabel(y_name + ' / $' + y_unit + '$')
        ax.set_xticks(mean_df[x_name].tolist())
        ax.grid(True)
        ax.use_sticky_edges = False
        ax.autoscale()
        ax.margins(x=0.1, y=0.1)
        if label:
            ax.legend([label])
        if save_file:
            if points == 0:
                points_name = 'all'
            else:
                points_name = str(points)
            plot_name = ''.join(x_name.split()) + '_' \
                        + ''.join(y_name.split()) + '_' \
                        + points_name + '-points.png'
            plt.savefig(os.path.join(self.work_dir, plot_name),
                        bbox_inches='tight')
        return ax

    def plot_series(self, column_name, start=0, stop=None, step=None):
        labels = []
        for item in self.data_objects:
            label = str(item.variable['value']) + ' $' \
                    + str(item.variable['unit']) + '$'
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
        x_unit = self.data_objects[0].units['Time']
        ax.set_xlabel('Time / $' + x_unit + '$')
        y_unit = self.data_objects[0].units[column_name]
        ax.set_ylabel(column_name + ' / $' + y_unit + '$')
        ax.legend(labels, loc='best')
        ax.grid(True)
        plot_name = ''.join(column_name.split()) + '_Time.png'
        plt.savefig(os.path.join(self.work_dir, plot_name), bbox_inches='tight')


class MultiCurve:
    """
    Class to combine and plot data from multiple single Curve objects
    """
    def __init__(self, base_dir, data_file_type, data_folder='Data',
                 dir_list=None):
        if dir_list:
            folder_list = [os.path.basename(os.path.normpath(name))
                           for name in dir_list]
        if not dir_list:
            path_list = [os.path.join(base_dir, name) for name
                         in os.listdir(base_dir)]
            dir_list = [name for name in path_list if os.path.isdir(name)]
            folder_list = [os.path.basename(os.path.normpath(name))
                           for name in dir_list]

        self.work_dir = base_dir

        # Create list of single curve objects
        self.curves = [Curve(data_dir, data_file_type, data_folder)
                       for data_dir in dir_list]
        file_names_list = [curve.data_file_names for curve in self.curves]
        self.data_file_names = [item for sublist in file_names_list
                                for item in sublist]
        # Create variable object describing variation between Curve objects
        self.variable = ea.InfoFile(os.path.join(base_dir, 'info.txt'),
                                    names=self.data_file_names)

    def __getitem__(self, key):
        return self.curves[key]

    # def plot_means(self, x_name, y_name, ax=None, points=0, print_plots=False):
    #     for curve in self.curves:
    #         var_data = self.variable.data
    #         var_name = self.variable.header['NAME'][0]
    #         label_series = \
    #             var_data[var_data['File Name'] == curve[0].file_name][var_name]
    #         label = label_series.iloc[0]
    #         ax = curve.plot_means(x_name, y_name, ax=ax, points=points,
    #                               label=label,  print_plots=print_plots)
    #         plt.show()
    #     return ax

    def plot_means(self, x_name, y_name, ax=None,
                   points=0, save_file=False):

        if x_name in self.variable.units:
            x_unit = self.variable.units[x_name]
        else:
            x_unit = self.curves[0].variable.units[x_name]
        y_unit = self.curves[0].data_objects[0].units[y_name]

        total_mean_df = self.mean_values(y_name, points)
        var_name = self.variable.header['NAME'][0]
        var_unit = self.variable.units[var_name]
        label_values = total_mean_df[var_name].unique()
        unit_label = ' $' + var_unit + '$'
        labels = [str(val) + unit_label for val in label_values]
        mean_dfs = \
            [total_mean_df[total_mean_df[var_name] == val].sort_values(x_name)
             for val in label_values]
        colors = list(islice(cycle(['k', 'b', 'r', 'g', 'y']), len(mean_dfs)))
        for i, df in enumerate(mean_dfs):
            ax = df.plot(x_name, y_name, ax=ax, marker='o',
                         markersize=5, color=colors[i], legend=False)

        ax.set_xlabel(x_name + ' / $' + x_unit + '$')
        ax.set_ylabel(y_name + ' / $' + y_unit + '$')
        ax.set_xticks(mean_dfs[0][x_name].tolist())
        ax.grid(True)
        ax.use_sticky_edges = False
        ax.autoscale()
        ax.margins(x=0.1, y=0.1)
        ax.legend(labels)
        if save_file:
            if points == 0:
                points_name = 'all'
            else:
                points_name = str(points)
            plot_name = ''.join(x_name.split()) + '_' \
                        + ''.join(y_name.split()) + '_' \
                        + points_name + '-points.png'
            plt.savefig(os.path.join(self.work_dir, plot_name),
                        bbox_inches='tight')
        return ax

    def mean_values(self, name='', points=0):
        mean_df = pd.concat([curve.mean_values(name, points)
                             for curve in self.curves])
        return self.variable.data.merge(mean_df)
