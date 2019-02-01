"""
Main program file to execute for processing data
"""

# Import required modules
import os
import electrochem_analysis as echem_ana
import electrochem_data as echem_data


work_dir = r"TestData\Gamry"
data_dir = os.path.join(work_dir, 'DataCollection')
info_path = os.path.join(work_dir, 'Info.txt')

curve = echem_ana.Curve(data_dir, 'DTA', info_path)
curve.plot_means('Zinc Concentration', 'Current', points=50)
curve.plot_series('Current')

work_dir = r"TestData\Biologic"
file_dir = os.path.join(work_dir, '1.4571_plasma.txt')
eclab_data = echem_data.DataFile(file_dir, 'EC-Lab')





