"""
Main program file to execute for processing data
"""
# Import required libraries
import src.electrochem_analysis as ea
from pathlib import Path
import os
import numpy as np

# Specify data directories
base_dir = Path(os.getcwd())/'TestData/Gamry'
folder_list = \
    ['0k8V_zn8_paa1_20181112',
     '0k8V_zn12_paa1_20181112',
     '0k8V_zn16_paa1_20181112']
dir_list = [base_dir/folder for folder in folder_list]

# Define variables, which are not provided directly by the measured data
multi_var = {
    'name': 'Zinc Concentration',
    'units': '$vol-\%$',
    'table': (('zn8_', 8.0),
              ('zn12_', 12.0),
              ('zn16_', 16.0))}

curve_var = {
    'name': 'Pump Speed',
    'units': '-',
    'table': (('ps10_', 10.0),
              ('ps50_', 50.0),
              ('ps100_', 100.0),
              ('ps200_', 200.0))}

# Set plotting properties
plot_props = {'xmultipler': 1.0,
              'yticks': np.linspace(0.0, 2000.0, 6),
              'linewidth': 1.0,
              'linestyle': '-',
              'markersize': '3.0',
              'color': ('k', 'b', 'r', 'g'),
              'ylabel': 'Current Density / $A/m^2$'}

plot_props['labels'] = \
    [curve_var['name'] + ': ' + str(value) + ' ' + curve_var['units']
     for value in [item[1] for item in curve_var['table']]]

# Set electrode surface area
electrode_area = {'name': 'electrode area', 'units': 'm²', 'value': 1.8e-3}

# Create single curve object
curve = ea.Curve(dir_list[0], 'DTA', variable=curve_var, ea=electrode_area)
plot_props['xlim'] = (0.0, 50.0)
plot_props['xlabel'] = 'Time / s'
curve.plot_series('Current Density', points=50, **plot_props, save_file=True)
#print([item.variable['value'] for item in curve.data_objects])
#print([item.file_name for item in curve.data_objects])


# Create multi curve object
multi_curve = ea.MultiCurve(base_dir, 'DTA', multi_variable=multi_var,
                            curve_variable=curve_var, ea=electrode_area)
plot_props['xlim'] = (0.0, 210.0)
plot_props['xticks'] = np.linspace(0.0, 200.0, 5)
plot_props['xlabel'] = 'Pump Speed / $-$'
plot_props['labels'] = \
    [multi_var['name'] + ': ' + str(value) + ' ' + multi_var['units']
     for value in [item[1] for item in multi_var['table']]]
multi_curve.plot_means('Pump Speed', 'Current Density',
                       points=50, save_file=True, **plot_props)
