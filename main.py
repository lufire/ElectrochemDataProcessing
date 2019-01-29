"""
Main program file to execute for processing data
"""

# Import required modules
import os
import electrochem_analysis as echem_ana

work_dir = r"TestData\Gamry"
data_dir = os.path.join(work_dir, 'DataCollection')
info_path = os.path.join(work_dir, 'Info.txt')

curve = echem_ana.Curve(data_dir, 'DTA', info_path)
curve.plot_means('Zinc Concentration', 'Current', points=50)
curve.plot_series('Current')




