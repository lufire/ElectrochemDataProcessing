"""
Main program file to execute for processing data
"""

# Import required modules
import os
import electrochem_analysis as echem_ana
import electrochem_data as echem_data


work_dir = r"TestData\Gamry"
data_dir = os.path.join(work_dir, 'DataCollection')

curve = echem_ana.Curve(data_dir, 'DTA', work_dir)
curve.plot_means('Zinc Concentration', 'Current', points=50)
curve.plot_series('Current')
curve.calculate_current_density()
curve.plot_means('Zinc Concentration', 'Current Density', points=50)

work_dir = r"TestData\Biologic"
file_dir = os.path.join(work_dir, '1.4571_plasma.txt')
eclab_data = echem_data.EChemDataFile(file_dir, 'EC-Lab')





