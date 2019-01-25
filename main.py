"""
Main program file to execute for processing data
"""

# Import required modules
import os
import input
import electrochem_analysis as echem_ana

work_dir = r"TestData/Gamry"
data_dir = os.path.join(work_dir, 'Data')
info_path = os.path.join(work_dir, 'Info.txt')

curve = echem_ana.Curve(data_dir, 'DTA', info_path)



