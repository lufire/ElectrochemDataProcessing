"""
Main program file to execute for processing data
"""
import sys
import os
sys.path.append(r'D:\Sonstiges\SourceCode\GitHub\ElectrochemDataProcessing')
# Import required modules
import electrochem_analysis as echem_ana
import electrochem_data as echem_data


work_dir = os.getcwd()
data_dir = os.path.join(work_dir, 'Data')

curve = echem_ana.Curve(data_dir, 'DTA', work_dir)
curve.calculate_current_density()
x_name = curve.variable.header['NAME'][0]
y_name = 'Current Density'
curve.plot_means(x_name, y_name, points=50)
curve.plot_series(y_name)






