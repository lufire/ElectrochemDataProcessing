"""
Main program file to execute for processing data
"""
import sys
import os
sys.path.append(r'D:\Sonstiges\SourceCode\GitHub\ElectrochemDataProcessing')
# Import required modules
import electrochem_analysis as echem_ana
import electrochem_data as echem_data


work_dir = os.path.join('TestData', 'Gamry')
data_dir = os.path.join(work_dir, 'DataCollection')

curve = echem_ana.Curve(data_dir, 'DTA', work_dir, read_var=True)
curve.plot_means('Zinc Concentration', 'Current', points=50)
curve.plot_series('Current')
curve.calculate_current_density()
curve.plot_means('Zinc Concentration', 'Current Density', points=50)

work_dir = os.path.join('TestData', 'Biologic')
file_dir = os.path.join(work_dir, '1.4571_plasma.txt')
eclab_data = echem_data.EChemDataFile(file_dir, 'EC-Lab')
