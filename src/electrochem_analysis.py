"""
Module containing classes for different analysis of the electrochemical data
"""

# Import required modules
import os
from abc import ABC, abstractmethod
import src.electrochem_data as ea
import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle, islice


class Curve:
    """
    Class to plot data from multiple data file objects
    """
    EA_STRS = ['esa', 'electrode_surface_area', 'electrode_area', 'ea']
    FILE_NAME_KEY = 'File Name'

    def __init__(self, base_dir, data_file_type, variable,
                 data_folder=None, **kwargs):
        self.data_folder = data_folder
        if data_folder:
            self.data_dir = os.path.join(base_dir, data_folder)
        else:
            self.data_dir = base_dir
        self.work_dir = base_dir
        self.electrode_area = None
        for item in self.EA_STRS:
            if item in kwargs:
                if isinstance(kwargs[item], dict):
                    self.electrode_area = kwargs[item]
                else:
                    raise TypeError('Electrode area must be provided as dict '
                                    'with "name", "value" and "units" as keys')

        # Find files in directory
        file_names = [name for name in os.listdir(self.data_dir)
                      if os.path.isfile(os.path.join(self.data_dir, name))]
        # Loop over list and find most common file extension
        ext_dict = {}
        for name in file_names:
            ext = name.rsplit('.', maxsplit=1)[1]
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
            path = os.path.join(self.data_dir, name)
            self.data_objects.append(ea.EChemDataFile(path,
                                                      data_file_type))
        self.variable = ea.InfoData(self.data_objects, variable, **kwargs)
        # Initialize current density column in the DataFile objects
        self.calculate_current_density(self.electrode_area)
        # Write variable data into data objects
        self.add_variable_to_objects()

    def __getitem__(self, key):
        return self.data_objects[key]

    def mean_values(self, points=0):
        mean_values = []
        file_names = []
        for item in self.data_objects:
            mean_values.append(item.data.iloc[-points:].mean())
            file_names.append(item.file_name)
        mean_df = pd.concat(mean_values, axis=1).T
        file_key = self.FILE_NAME_KEY
        mean_df[file_key] = file_names
        if self.variable.variable_name in self.data_objects[0].data:
            return mean_df
        else:
            merge_name = self.variable.MERGE_NAME
            pat = "|".join(self.variable.data[merge_name])
            mean_df.insert(0, merge_name,
                           mean_df[file_key].str.extract('(' + pat + ')',
                                                         expand=False))
            if mean_df[merge_name].isna().any():
                raise ValueError("Merging between variable and mean data "
                                 "failed. Check spelling in table, bounds or "
                                 "info_file.")
            return self.variable.data.merge(mean_df).drop(columns=merge_name)

    def calculate_current_density(self, electrode_area=None):
        if not electrode_area:
            electrode_area = dict()
            electrode_area['name'] = 'Electrode Surface Area'
            key = 'ELECTRODE SURFACE AREA'
            if hasattr(self.variable, 'header') and key in self.variable.header:
                electrode_area['value'] = \
                    float(self.variable.header[key][0])
                electrode_area['units'] = \
                    str(self.variable.header[key][1])
            else:
                electrode_area['value'] = float(input('Provide value for '
                                                      'electrode surface '
                                                      'area:'))
                electrode_area['units'] = input('Provide unit for electrode '
                                                'surface area:')
        for item in self.data_objects:
            item.calculate_current_density(electrode_area)

    def plot_means(self, x_name, y_name, ax=None,
                   points=0, label=None, limits=None, save_file=False):
        mean_df = self.mean_values(points)
        if x_name in self.variable.units:
            x_unit = self.variable.units[x_name]
        else:
            x_unit = self.data_objects[0].units[x_name]
        y_unit = self.data_objects[0].units[y_name]
        ax = mean_df.plot(x_name, y_name, ax=ax, color='k', marker='o',
                          markersize=6, legend=False)
        ax.set_xlabel(x_name + ' / $' + x_unit + '$')
        ax.set_ylabel(y_name + ' / $' + y_unit + '$')
        ax.set_xticks(mean_df[x_name].tolist())
        if isinstance(limits, (list, tuple)):
            ax.set_xlim(limits[0])
            ax.set_ylim(limits[1])
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

    def plot_series(self, column_name, start=0, stop=None, step=1, points=None,
                    ax=None, save_file=None, **kwargs):
        try:
            labels = kwargs['labels']
        except KeyError:
            raise KeyError('Labels must be provided for time series plots')
        colors = \
            kwargs.get('color', list(islice(cycle(['k', 'b', 'r', 'g', 'y']),
                                            len(self.data_objects))))
        linestyles = kwargs.get('linestyle', '-')

        for i, data_object in enumerate(self.data_objects):
            try:
                color = colors[i]
            except TypeError:
                color = colors
            try:
                linestyle = linestyles[i]
            except (TypeError, IndexError) as e:
                linestyle = linestyles
            if points:
                stop = len(data_object.data.index)
                start = stop - points
            elif stop and stop <= start:
                stop = len(data_object.data.index)
            slicer = slice(start, stop, step)
            column_name_scaled = column_name
            df = data_object.data
            time_name_shifted = 'Time Shifted'
            df[time_name_shifted] = df['Time']-df['Time'].iloc[start]
            if 'ymultiplier' in kwargs:
                column_name_scaled = column_name + ' Scaled'
                df[column_name_scaled] = df[column_name] * kwargs['ymultiplier']
            ax = df.iloc[slicer].plot(time_name_shifted, column_name_scaled,
                                      ax=ax, marker=kwargs.get('marker', 'o'),
                                      markersize=kwargs.get('markersize', 5.0),
                                      linewidth=kwargs.get('linewidth', 1.0),
                                      linestyle=linestyle,
                                      color=color)
        x_unit = self.data_objects[0].units['Time']
        ax.set_xlabel(kwargs.get('xlabel', 'Time / $' + x_unit + '$'))
        y_unit = self.data_objects[0].units[column_name]
        ax.set_ylabel(kwargs.get('ylabel', column_name + ' / $' + y_unit + '$'))
        ax.grid(True)
        ax.autoscale()
        ax.use_sticky_edges = False
        if 'xlim' in kwargs:
            ax.set_xlim(kwargs['xlim'])
        if 'ylim' in kwargs:
            ax.set_ylim(kwargs['ylim'])
        if 'xticks' in kwargs:
            ax.set_xticks(kwargs['xticks'])
        if 'yticks' in kwargs:
            ax.set_yticks(kwargs['yticks'])
        if 'margins' in kwargs:
            ax.margins(x=kwargs['margins'][0], y=kwargs['margins'][1])
        ax.legend(labels, loc='best')
        if save_file:
            points_name = '_start-' + str(start) + '_stop-' + str(stop)
            plot_name = ''.join(column_name.split()) + '_Time_' \
                        + points_name + '.png'

            plt.savefig(os.path.join(self.work_dir, plot_name),
                        bbox_inches='tight')
        return ax

    def add_variable_to_objects(self):
        # Write variable data into data objects
        if isinstance(self.variable.data, pd.DataFrame):
            var_data = self.variable.data
            var_name = var_data.columns[1]
            var_values = var_data[var_name].tolist()

            merge_names = var_data[self.variable.MERGE_NAME].tolist()
            file_names = [item.file_name for item in self.data_objects]
            for i, name in enumerate(merge_names):
                try:
                    index = \
                        [i for i, s in enumerate(file_names) if name in s][0]
                except IndexError:
                    raise IndexError('Merge name ' + name + ' could not be '
                                     'found in ' + file_names)
                self.data_objects[index].variable = \
                    {'name': var_name,
                     'units': self.variable.units[var_name]}
                self.data_objects[index].variable['value'] = var_values[i]

            # Sort data objects according to variable values
            var_values = [item.variable['value'] for item in self.data_objects]
            self.data_objects = \
                [x for _, x in sorted(zip(var_values, self.data_objects))]


class MultiCurve(ABC):
    """
    Class to combine and plot data from multiple single Curve objects
    """
    EA_STRS = ['esa', 'electrode_surface_area', 'electrode_area', 'ea']

    def __init__(self, base_dir, data_file_type, multi_variable=None,
                 curve_variable=None, dir_list=None,
                 data_folder=None, **kwargs):
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
        self.electrode_area = None
        for item in self.EA_STRS:
            if item in kwargs:
                if isinstance(kwargs[item], dict):
                    self.electrode_area = kwargs[item]
                else:
                    raise TypeError('Electrode area must be provided as dict '
                                    'with "name", "value" and "units" as keys')

        # Create list of single curve objects
        self.curves = [Curve(data_dir, data_file_type,
                             variable=curve_variable,
                             data_folder=data_folder,
                             electrode_area=self.electrode_area)
                       for data_dir in dir_list]
        data_objects = [item for data_objects in self.curves
                        for item in data_objects]
        # Create variable object describing variation between Curve objects
        self.variable = ea.InfoData(data_objects, multi_variable, **kwargs)

    def __getitem__(self, key):
        return self.curves[key]

    def plot_means(self, x_name, y_name, ax=None,
                   points=0, save_file=False, **kwargs):
        if x_name in self.variable.units:
            x_unit = self.variable.units[x_name]
        elif x_name in self.curves[0].variable.units:
            x_unit = self.curves[0].variable.units[x_name]
        else:
            x_unit = self.curves[0].data_objects[0].units[x_name]
            
        if y_name in self.variable.units:
            y_unit = self.variable.units[y_name]
        elif y_name in self.curves[0].variable.units:
            y_unit = self.curves[0].variable.units[y_name]
        else:
            y_unit = self.curves[0].data_objects[0].units[y_name]

        total_mean_df = self.mean_values(points)
        var_name = self.variable.variable_name
        var_unit = self.variable.units[var_name]
        label_values = total_mean_df[var_name].unique()
        unit_label = ' $' + var_unit + '$'
        labels = [str(val) + unit_label for val in label_values]
        labels = kwargs.get('labels', labels)
        mean_dfs = \
            [total_mean_df[total_mean_df[var_name] == val].sort_values(x_name)
             for val in label_values]
        colors = \
            kwargs.get('color', list(islice(cycle(['k', 'b', 'r', 'g', 'y']),
                                            len(mean_dfs))))

        linestyles = kwargs.get('linestyle', '-')
        if len(mean_dfs) > 0:
            for i, df in enumerate(mean_dfs):
                try:
                    linestyle = linestyles[i]
                except (TypeError, IndexError) as e:
                    linestyle = linestyles
                xname_scaled = x_name
                yname_scaled = y_name
                if 'xmultiplier' in kwargs:
                    xname_scaled = x_name + ' Scaled'
                    df[xname_scaled] = df[x_name]*kwargs['xmultiplier']
                if 'ymultiplier' in kwargs:
                    yname_scaled = y_name + ' Scaled'
                    df[yname_scaled] = df[y_name]*kwargs['ymultiplier']
                ax = df.plot(xname_scaled, yname_scaled, ax=ax,
                             marker=kwargs.get('marker', 'o'),
                             markersize=kwargs.get('markersize', 5.0),
                             linewidth=kwargs.get('linewidth', 1.0),
                             linestyle=linestyle,
                             color=colors[i],  legend=False)
        else:
            raise ValueError("No data points found")

        ax.set_xlabel(kwargs.get('xlabel', x_name + ' / $' + x_unit + '$'))
        ax.set_ylabel(kwargs.get('ylabel', y_name + ' / $' + y_unit + '$'))
        ax.grid(True)
        ax.use_sticky_edges = False
        ax.autoscale()
        if 'margins' in kwargs:
            ax.margins(x=kwargs['margins'][0], y=kwargs['margins'][1])
        if 'xlim' in kwargs:
            ax.set_xlim(kwargs['xlim'])
        if 'ylim' in kwargs:
            ax.set_ylim(kwargs['ylim'])
        if 'xticks' in kwargs:
            ax.set_xticks(kwargs['xticks'])
        if 'yticks' in kwargs:
            ax.set_yticks(kwargs['yticks'])

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

    def mean_values(self, points=0):
        mean_df = pd.concat([curve.mean_values(points)
                             for curve in self.curves])
        if self.variable.variable_name in self.curves[0].data_objects[0].data:
            return mean_df
        else:
            file_key = self.curves[0].FILE_NAME_KEY
            merge_key = self.variable.MERGE_NAME
            pat = "|".join(self.variable.data[merge_key])
            mean_df.insert(0, merge_key,
                           mean_df[file_key].str.extract('(' + pat + ')',
                                                         expand=False))
            if mean_df[merge_key].isna().any():
                raise ValueError("Merging between variable and mean data "
                                 "failed. Check spelling in table, bounds or "
                                 "info_file.")
            return self.variable.data.merge(mean_df).drop(columns=merge_key)
